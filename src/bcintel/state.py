"""Bot idempotency store — a thin interface over a deep module.

The append-only JSONL corpus records what *happened upstream*; this records what
the *bot itself* has already done, keyed by an idempotency token per submission.
It mutates, so it lives apart from the corpus in a small SQLite file (stdlib, no
new dep, no DuckDB). Callers use only seen()/record()/close() — all SQL hides here.

The token is `(repo, issue, sha)`: a new build sha for an issue is a new key, so
a version bump re-triggers a briefing while a repeat run over the same sha skips.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

_SCHEMA = """
CREATE TABLE IF NOT EXISTS bot_runs (
    repo TEXT, issue_number INTEGER, commit_sha TEXT,
    stage TEXT, action TEXT, status TEXT, briefing_path TEXT, updated_at TEXT,
    review_md TEXT,
    PRIMARY KEY (repo, issue_number, commit_sha)
)
"""


class State:
    def __init__(self, path):
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        self._con = sqlite3.connect(str(p))
        self._con.execute(_SCHEMA)
        # migrate older dbs that predate review_md
        cols = {r[1] for r in self._con.execute("PRAGMA table_info(bot_runs)")}
        if "review_md" not in cols:
            self._con.execute("ALTER TABLE bot_runs ADD COLUMN review_md TEXT")
        self._con.commit()

    def seen(self, repo, issue, sha) -> bool:
        row = self._con.execute(
            "SELECT 1 FROM bot_runs WHERE repo=? AND issue_number=? AND commit_sha=?",
            (repo, issue, sha)).fetchone()
        return row is not None

    def last_review(self, repo, issue):
        """Most recent stored review for an issue: (commit_sha, review_md) or None.

        Call before record() so a re-review can diff against the prior one.
        """
        row = self._con.execute(
            """SELECT commit_sha, review_md FROM bot_runs
               WHERE repo=? AND issue_number=? AND review_md IS NOT NULL
               ORDER BY updated_at DESC LIMIT 1""",
            (repo, issue)).fetchone()
        return (row[0], row[1]) if row else None

    def record(self, repo, issue, sha, *, stage, action, status="done",
               briefing_path=None, review_md=None) -> None:
        self._con.execute(
            """INSERT INTO bot_runs
                 (repo, issue_number, commit_sha, stage, action, status,
                  briefing_path, updated_at, review_md)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT (repo, issue_number, commit_sha) DO UPDATE SET
                 stage=excluded.stage, action=excluded.action, status=excluded.status,
                 briefing_path=excluded.briefing_path, updated_at=excluded.updated_at,
                 review_md=excluded.review_md""",
            (repo, issue, sha, stage, action, status, briefing_path,
             datetime.now(timezone.utc).isoformat(), review_md))
        self._con.commit()

    def close(self) -> None:
        self._con.close()
