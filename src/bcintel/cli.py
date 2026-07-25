"""bcintel — ingest & query the Bioconductor submission-tracker corpus.

    bcintel fetch [--repo O/R ...] [--limit N] [--concurrency C]
    bcintel sql "SELECT ..."
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from . import bot, db
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

    a = p.parse_args(argv)
    _load_dotenv()
    if a.cmd == "fetch":
        fetch(a.repo or REPOS, DATA, a.limit, a.concurrency)
    elif a.cmd == "sql":
        print(db.connect().sql(a.query))
    elif a.cmd == "bot":
        bot.run(a.repo or REPOS, DATA, a.out, use_llm=not a.no_llm, limit=a.limit,
                force=a.force)


if __name__ == "__main__":
    main()
