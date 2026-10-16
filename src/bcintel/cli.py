"""bcintel — ingest & query the Bioconductor submission-tracker corpus.

    bcintel fetch [--repo O/R ...] [--limit N] [--concurrency C]
    bcintel sql "SELECT ..."
    bcintel dashboard [--out site]
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from . import bot, dashboard, db, review
from .fetch import CONCURRENCY, REPOS, fetch

DATA = Path("data")


def _load_dotenv(path=".env"):
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip().removeprefix("export ").strip()
        if not line or line.startswith("#"):
            continue
        k, _, v = line.partition("=")
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in os.environ:  # real env wins over .env
            os.environ[k] = v


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="bcintel", description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    pf = sub.add_parser("fetch", help="backfill issues + timelines to JSONL")
    pf.add_argument("--repo", action="append", metavar="O/R",
                    help="repo (repeatable; default: both trackers)")
    pf.add_argument("--limit", type=int, help="max NEW issues per repo (for testing)")
    pf.add_argument("--concurrency", type=int, default=CONCURRENCY,
                    help=f"parallel producers (default: {CONCURRENCY})")

    ps = sub.add_parser("sql", help="run DuckDB SQL over the JSONL")
    ps.add_argument("query", help="SQL to execute")

    pb = sub.add_parser("bot", help="dry-run advisory bot: write Markdown briefings per open issue")
    pb.add_argument("--repo", action="append", metavar="O/R",
                    help="repo (repeatable; default: both trackers)")
    pb.add_argument("--out", default="bot_out", help="output directory (default: bot_out)")
    pb.add_argument("--no-llm", action="store_true", help="skip the Gemini judgment layer")
    pb.add_argument("--limit", type=int, help="max issues per repo (for testing / cost)")
    pb.add_argument("--force", action="store_true",
                    help="re-brief every issue, bypassing the idempotency store")

    pr = sub.add_parser("review",
                        help="clone each open submission and write a static review comment")
    pr.add_argument("--repo", action="append", metavar="O/R",
                    help="repo (repeatable; default: both trackers)")
    pr.add_argument("--out", default="bot_out", help="output directory (default: bot_out)")
    pr.add_argument("--limit", type=int, help="max NEW reviews per repo (for testing / cost)")
    pr.add_argument("--force", action="store_true",
                    help="re-review even if the current sha was already reviewed")
    pr.add_argument("--patch", action="store_true",
                    help="also draft a proposed-PR markdown with safe metadata fixes")
    pr.add_argument("--issue", type=int, help="review only this issue number")

    pc = sub.add_parser("cycle",
                        help="one reactive tick: fetch the corpus, then review changed submissions")
    pc.add_argument("--repo", action="append", metavar="O/R",
                    help="repo (repeatable; default: both trackers)")
    pc.add_argument("--out", default="bot_out", help="output directory (default: bot_out)")
    pc.add_argument("--limit", type=int, help="max NEW reviews per repo")
    pc.add_argument("--patch", action="store_true", help="also draft proposed PRs")
    pc.add_argument("--site", default="site", help="dashboard output directory (default: site)")

    pg = sub.add_parser("gate1-eval", help="score submissions' DESCRIPTIONs with Clef (Gate 1 fit)")
    pg.add_argument("--split", choices=["dev", "test"], default="dev")
    pg.add_argument("--max-accepted", type=int, default=40,
                    help="cap on accepted (positive) examples (default: 40)")
    pg.add_argument("--model", choices=["clef", "clef-flash"], default="clef")
    pg.add_argument("--note", default="", help="free-text note for the ledger line")

    pv = sub.add_parser("gate1-v3", help="Gate 1 v3: code-level features + Clef (see gate1code)")
    pv.add_argument("step", choices=["fetch", "index", "features", "eval-features", "eval-clef"])
    pv.add_argument("--max-clean", type=int, default=600, help="clean-accept sample size")
    pv.add_argument("--split", choices=["dev", "test"], default="dev")
    pv.add_argument("--max-n", type=int, help="cap examples scored by Clef")
    pv.add_argument("--note", default="")

    pd = sub.add_parser("dashboard", help="build the static reviewer dashboard")
    pd.add_argument("--out", default="site", help="output directory (default: site)")

    a = p.parse_args(argv)
    _load_dotenv()
    if a.cmd == "fetch":
        fetch(a.repo or REPOS, DATA, a.limit, a.concurrency)
    elif a.cmd == "sql":
        print(db.connect().sql(a.query))
    elif a.cmd == "bot":
        bot.run(a.repo or REPOS, DATA, a.out, use_llm=not a.no_llm, limit=a.limit,
                force=a.force)
    elif a.cmd == "review":
        review.run(a.repo or REPOS, DATA, a.out, limit=a.limit, force=a.force,
                   patch=a.patch, only_issue=a.issue)
    elif a.cmd == "cycle":
        repos = a.repo or REPOS
        fetch(repos, DATA, None, CONCURRENCY)
        review.run(repos, DATA, a.out, limit=a.limit, patch=a.patch)
        dashboard.build(DATA, Path(a.site))
    elif a.cmd == "gate1-eval":
        from . import gate1
        out = gate1.run(a.split, a.max_accepted, a.model, note=a.note)
        print(out / "metrics.json")
        print((out / "metrics.json").read_text())
    elif a.cmd == "gate1-v3":
        from . import gate1code as g
        if a.step == "fetch":
            print(g.fetch(g.sample(a.max_clean)))
        elif a.step == "index":
            from collections import Counter
            res = g.index()
            print(Counter(v.split(":")[0] for v in res.values()))
        elif a.step == "features":
            print(len(g.features()), "packages with features")
        elif a.step == "eval-features":
            print((g.eval_features(a.note) / "metrics.json").read_text())
        else:
            print((g.eval_clef(a.split, max_n=a.max_n, note=a.note) / "metrics.json").read_text())
    elif a.cmd == "dashboard":
        print(dashboard.build(DATA, Path(a.out)) / "index.html")


if __name__ == "__main__":
    main()
