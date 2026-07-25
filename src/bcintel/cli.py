"""bcintel — ingest & query the Bioconductor submission-tracker corpus.

    bcintel fetch [--repo O/R ...] [--limit N] [--concurrency C]
    bcintel sql "SELECT ..."
"""
from __future__ import annotations

import argparse
from pathlib import Path

from . import db
from .fetch import CONCURRENCY, REPOS, fetch

DATA = Path("data")


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

    a = p.parse_args(argv)
    if a.cmd == "fetch":
        fetch(a.repo or REPOS, DATA, a.limit, a.concurrency)
    elif a.cmd == "sql":
        print(db.connect().sql(a.query))


if __name__ == "__main__":
    main()
