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
       assigned_at, reviewer_last, first_assigned, team_last, team_last_by,
       comments_since, pushes_since, build, stage,
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
REPORTS = """
SELECT b.issue_number, b.comment_id, b.posted_at, b.kind, b.version, b.worst,
       b.run_url, b.staging_url, b.runiverse_url
FROM build_reports b JOIN issues i ON i.repo = b.repo AND i.number = b.issue_number
WHERE b.repo = $repo AND i.state = 'open' ORDER BY b.issue_number, b.posted_at
"""
CHECKS = """
SELECT c.comment_id, c.platform, c.r_version, c.status, c.url
FROM checks c JOIN issues i ON i.repo = c.repo AND i.number = c.issue_number
WHERE c.repo = $repo AND i.state = 'open' ORDER BY c.comment_id, c.platform
"""
SOURCES = """
SELECT p.issue_number, p.package_name, p.source_url
FROM packages p JOIN issues i ON i.repo = p.repo AND i.number = p.issue_number
WHERE p.repo = $repo AND i.state = 'open'
"""
# Weekly replay of the reviewer_queue rule at past instants t = now, now-7d, ...:
# backlog sizes and the reviewer's-move wait as they stood then. A reviewer is anyone
# ever assigned to the issue (assignees at close aren't the assignees back then).
# ponytail: ignores reopen and unassign events; fine for backlog-level trends.
TREND = """
WITH pts AS (
  SELECT $now::TIMESTAMP - k * INTERVAL 7 DAY AS t
  FROM range(0, (SELECT date_diff('day', min(created_at), $now::TIMESTAMP) // 7 + 1
                 FROM issues WHERE repo = $repo)) r(k)
), asg AS MATERIALIZED (
  SELECT issue_number, assignee, created_at FROM events WHERE repo = $repo AND event = 'assigned'
), act AS MATERIALIZED (
  SELECT a.issue_number, a.occurred_at, a.role = 'submitter' AS by_sub,
         a.kind = 'comment' AND EXISTS (SELECT 1 FROM asg WHERE asg.issue_number = a.issue_number
                                        AND asg.assignee = a.who) AS by_rev
  FROM activity a WHERE a.repo = $repo
), st AS (
  SELECT p.t, i.number,
    (SELECT min(created_at) FROM asg
     WHERE asg.issue_number = i.number AND asg.created_at <= p.t) AS first_assigned,
    (SELECT max(occurred_at) FROM act WHERE act.issue_number = i.number AND by_rev
       AND occurred_at <= p.t) AS team_last
  FROM pts p JOIN issues i ON i.repo = $repo AND i.created_at <= p.t
    AND (i.closed_at IS NULL OR i.closed_at > p.t)
), w AS (
  SELECT *, first_assigned IS NOT NULL AND (team_last IS NULL OR sub_first IS NOT NULL) AS rt,
    floor(epoch(t - CASE WHEN team_last IS NULL THEN first_assigned
                         WHEN sub_first IS NOT NULL THEN sub_first
                         ELSE team_last END) / 86400) AS wait
  FROM (SELECT *, (SELECT min(occurred_at) FROM act WHERE act.issue_number = st.number AND by_sub
                     AND occurred_at > coalesce(team_last, first_assigned)
                     AND occurred_at <= st.t) AS sub_first FROM st)
)
SELECT p.t,
  count(w.number) AS open,
  count(w.number) FILTER (WHERE w.first_assigned IS NULL) AS unassigned,
  count(w.number) FILTER (WHERE w.rt) AS reviewer_move,
  count(w.number) FILTER (WHERE w.rt AND w.wait > 28) AS over28,
  median(w.wait) FILTER (WHERE w.rt) AS median_wait,
  quantile_cont(w.wait, 0.9) FILTER (WHERE w.rt) AS p90_wait,
  (SELECT count(*) FROM issues i WHERE i.repo = $repo
     AND i.created_at > p.t - INTERVAL 7 DAY AND i.created_at <= p.t) AS opened,
  (SELECT count(*) FROM issues i WHERE i.repo = $repo
     AND i.closed_at > p.t - INTERVAL 7 DAY AND i.closed_at <= p.t) AS closed
FROM pts p LEFT JOIN w ON w.t = p.t
GROUP BY p.t ORDER BY p.t
"""


def _rows(con, sql: str, **params) -> list[dict]:
    cur = con.execute(sql, {"repo": REPO, **params})
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r, strict=True)) for r in cur.fetchall()]


def _read_json(p: Path) -> list:
    return json.loads(p.read_text()) if p.exists() else []


def _enc(o):
    # Timestamps from DuckDB are naive UTC; tag them so the browser parses UTC.
    return o.isoformat() + "Z" if isinstance(o, datetime) else str(o)


RANK = {"OK": 0, "NOTE": 2, "WARNING": 3, "ERROR": 4}  # anything else ranks as UNKNOWN (1)


def _worst(statuses) -> str | None:
    return max(statuses, key=lambda s: RANK.get(s, 1), default=None)


def _live(pkgs: list[dict]) -> dict[str, dict]:
    """r-universe's current results per staging package (lower-cased name)."""
    out = {}
    for p in pkgs:
        jobs = [{"platform": j.get("config"), "r_version": j.get("r"), "status": j.get("check")}
                for j in p.get("_jobs") or [] if j.get("check")]
        t = (p.get("_commit") or {}).get("time")
        out[p["Package"].lower()] = {
            "version": p.get("Version"), "jobs": jobs, "worst": _worst(j["status"] for j in jobs),
            "commit_time": datetime.fromtimestamp(t, timezone.utc).isoformat() if t else None}
    return out


def _issue_info(con, live: dict[str, dict] | None = None) -> dict[int, dict]:
    """Per open issue: package links, the latest build report with its per-platform
    checks, and the version history (invalid bumps included, flagged by kind)."""
    checks: dict[int, list] = {}
    for c in _rows(con, CHECKS):
        checks.setdefault(c.pop("comment_id"), []).append(c)
    info = {r["issue_number"]: {"package": r["package_name"], "source_url": r["source_url"],
                                "latest_build": None, "versions": []}
            for r in _rows(con, SOURCES)}
    for r in _rows(con, REPORTS):
        it = info.setdefault(r["issue_number"], {"latest_build": None, "versions": []})
        it["versions"].append({k: r[k] for k in ("version", "posted_at", "kind", "worst")})
        if r["kind"] != "invalid_version":
            it["latest_build"] = {**{k: v for k, v in r.items() if k != "issue_number"},
                                  "checks": checks.get(r["comment_id"], [])}
    for it in info.values():
        lv = (live or {}).get((it.get("package") or "").lower())
        it["live"] = lv
        b = it["latest_build"]
        # The issue's report no longer matches r-universe (newer version or a re-run).
        it["live_differs"] = bool(lv and b and lv["jobs"] and
                                  (lv["version"] != b["version"] or lv["worst"] != b["worst"]))
    return info


def trend(con, now: datetime | None = None) -> list[dict]:
    """Weekly backlog and reviewer's-move wait, oldest first; the last point is now."""
    now = now or datetime.now(timezone.utc).replace(tzinfo=None)  # data timestamps are naive UTC
    return _rows(con, TREND, now=now)


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
        "issues": _issue_info(con, _live(_read_json(data_dir / "runiverse" / "biocstaging.json"))),
        "trend": trend(con),
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
