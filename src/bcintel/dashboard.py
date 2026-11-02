"""Reviewer dashboard — a static site: `data.json` + a hash-routed `index.html`.

Read-only. Answers "whose move is it, and for how long" per reviewer, from the
`reviewer_queue` / `activity` views. Rebuilt on every `cycle` tick; serve the
output directory with any static file server.
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from . import db

REPO = "Bioconductor/BiocContributions"  # new tracker only; legacy is history
# ponytail: placeholder AI review per open issue so the app can be built around
# i/<n>.review.md; replace with the real review output once the parsers are fixed.
REVIEW_STUB = "REVIEW BODY HERE\n"

QUEUE = """
SELECT issue_number, title, submitter, reviewer, reviewer_turn, waiting_since,
       assigned_at, reviewer_last, comments_since, pushes_since, build, stage,
       stage_since, last_comment
FROM reviewer_queue WHERE repo = $repo
ORDER BY reviewer_turn DESC, waiting_since
"""
UNASSIGNED = """
SELECT number AS issue_number, title, author AS submitter, created_at, labels
FROM issues WHERE repo = $repo AND state = 'open' AND len(assignees) = 0
ORDER BY created_at
"""
THREAD = """
WITH open AS (SELECT number FROM issues WHERE repo = $repo AND state = 'open')
SELECT issue_number, id, created_at, 'comment' AS kind, author AS who, is_bot, body
FROM comments WHERE repo = $repo AND issue_number IN (SELECT number FROM open)
UNION ALL
SELECT issue_number, id, created_at, event, actor, actor LIKE '%[bot]',
       coalesce(label, assignee)
FROM events WHERE repo = $repo AND issue_number IN (SELECT number FROM open)
  AND event IN ('labeled', 'unlabeled', 'assigned', 'unassigned', 'closed', 'reopened')
ORDER BY issue_number, created_at
"""


def _rows(con, sql: str) -> list[dict]:
    cur = con.execute(sql, {"repo": REPO})
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r, strict=True)) for r in cur.fetchall()]


def _enc(o):
    # Timestamps from DuckDB are naive UTC; tag them so the browser parses UTC.
    return o.isoformat() + "Z" if isinstance(o, datetime) else str(o)


def build(data_dir: Path, out_dir: Path) -> Path:
    con = db.connect(str(data_dir))
    threads: dict[int, list] = {}
    for r in _rows(con, THREAD):
        threads.setdefault(r.pop("issue_number"), []).append(r)
    data = {
        "repo": REPO,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "queue": _rows(con, QUEUE),
        "unassigned": _rows(con, UNASSIGNED),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "data.json").write_text(json.dumps(data, default=_enc))
    # One file per issue, fetched when its page opens (keeps data.json small).
    (out_dir / "i").mkdir(exist_ok=True)
    for n, thread in threads.items():
        (out_dir / "i" / f"{n}.json").write_text(json.dumps(thread, default=_enc))
        (out_dir / "i" / f"{n}.review.md").write_text(REVIEW_STUB)
    shutil.copy(Path(__file__).with_name("dashboard.html"), out_dir / "index.html")
    return out_dir
