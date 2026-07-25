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
    PRIMARY KEY (repo, issue_number, commit_sha)
)
"""


class State:
    def __init__(self, path):
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        self._con = sqlite3.connect(str(p))
        self._con.execute(_SCHEMA)
        self._con.commit()

    def seen(self, repo, issue, sha) -> bool:
        row = self._con.execute(
            "SELECT 1 FROM bot_runs WHERE repo=? AND issue_number=? AND commit_sha=?",
            (repo, issue, sha)).fetchone()
        return row is not None

    def record(self, repo, issue, sha, *, stage, action, status="done",
               briefing_path=None) -> None:
        self._con.execute(
            """INSERT INTO bot_runs
                 (repo, issue_number, commit_sha, stage, action, status,
                  briefing_path, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT (repo, issue_number, commit_sha) DO UPDATE SET
                 stage=excluded.stage, action=excluded.action, status=excluded.status,
                 briefing_path=excluded.briefing_path, updated_at=excluded.updated_at""",
            (repo, issue, sha, stage, action, status, briefing_path,
             datetime.now(timezone.utc).isoformat()))
        self._con.commit()

    def close(self) -> None:
        self._con.close()
