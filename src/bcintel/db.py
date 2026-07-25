"""DuckDB views over the raw JSONL. No import step — query the files directly.

comments and events are both derived from the per-issue timeline stream.
`union_by_name` tolerates the two repos having slightly different JSON shapes.
"""
from __future__ import annotations

import duckdb

# {base} is the data directory (default "data"); glob picks up both repo subdirs.
# Raw string so regex backrefs (\1) and classes (\s, \.) reach DuckDB intact.
VIEWS = r"""
CREATE OR REPLACE VIEW issues_raw AS
  SELECT * FROM read_json_auto('{base}/*/issues.jsonl', union_by_name=true);
CREATE OR REPLACE VIEW timeline_raw AS
  SELECT * FROM read_json_auto('{base}/*/timeline.jsonl',
                               union_by_name=true, ignore_errors=true);

CREATE OR REPLACE VIEW issues AS
SELECT _repo AS repo, number, title, state, state_reason,
       user.login AS author, created_at, updated_at, closed_at,
       [l.name FOR l IN labels] AS labels,
       [a.login FOR a IN assignees] AS assignees,
       comments AS comment_count, body
FROM issues_raw
QUALIFY row_number() OVER (PARTITION BY _repo, number ORDER BY updated_at DESC) = 1;

CREATE OR REPLACE VIEW comments AS
SELECT _repo AS repo, _issue AS issue_number, id,
       user.login AS author, author_association, created_at, updated_at,
       user.login IN ('bioc-issue-bot','github-actions[bot]') AS is_bot, body
FROM timeline_raw
WHERE event = 'commented'
QUALIFY row_number() OVER (PARTITION BY id ORDER BY updated_at DESC) = 1;

-- Assumes the timeline contains at least one labeled/assigned event so DuckDB
-- infers the label/assignee/actor columns. True for both target repos.
CREATE OR REPLACE VIEW events AS
SELECT _repo AS repo, _issue AS issue_number, id, event,
       coalesce(actor.login, user.login) AS actor,
       label.name AS label, assignee.login AS assignee, created_at
FROM timeline_raw
QUALIFY row_number() OVER (PARTITION BY _issue, event, coalesce(id, 0), coalesce(created_at, '')
                          ORDER BY created_at DESC) = 1;

-- Consecutive label changes per issue — the raw edges of the lifecycle state
-- machine. Includes build-status labels (OK/ERROR/…); filter to the stage set
-- ('1. awaiting moderation', 'pre-check passed', 'pre-review',
--  '2. review in progress', '3a'..'3e') to get the review state machine.
CREATE OR REPLACE VIEW label_transitions AS
SELECT repo, issue_number,
       lag(label) OVER (PARTITION BY repo, issue_number ORDER BY created_at) AS from_label,
       label AS to_label,
       created_at AS changed_at
FROM events
WHERE event = 'labeled';

-- ── Derived views (parsed from issue bodies + bot comments) ──────────────────

-- One row per submission: package name, source repo, and final outcome.
-- package_name comes from the "Repository:" URL in the body, falling back to the
-- title with any "(inactive)"/"(declined)" prefix stripped.
CREATE OR REPLACE VIEW packages AS
WITH x AS (
  SELECT repo, number, author, title, state, labels, created_at, closed_at,
         regexp_extract(body, '[Rr]epository:\s*(\S+)', 1) AS source_url
  FROM issues
)
SELECT repo, number AS issue_number, author AS submitter, source_url,
       coalesce(nullif(regexp_replace(source_url, '^.*/([^/]+?)(\.git)?$', '\1'), ''),
                regexp_replace(title, '^\(\w+\)\s*', '')) AS package_name,
       CASE WHEN list_contains(labels, '3a. accepted')                 THEN 'accepted'
            WHEN list_contains(labels, '3b. declined')                 THEN 'declined'
            WHEN list_contains(labels, '3c. inactive')                 THEN 'inactive'
            WHEN list_contains(labels, '3d. needs interop')            THEN 'needs_interop'
            WHEN list_contains(labels, '3e. pending pre-review changes') THEN 'pending'
            WHEN state = 'open'                                        THEN 'in_progress'
            ELSE 'unknown' END AS outcome,
       created_at, closed_at
FROM x;

-- Per-build result posted by the bot: the state string (comma-separated across
-- platforms, e.g. "skipped, ERROR") and the build-report URL, in time order.
CREATE OR REPLACE VIEW builds AS
SELECT repo, issue_number, created_at,
       regexp_extract(body, 'build results were: "([^"]+)"', 1) AS state,
       regexp_extract(body, '(https?://\S+buildreport\S+?\.html)', 1) AS report_url
FROM comments
WHERE body LIKE '%build results were%';

-- The "AdditionalPackage: <url>" bundling — one issue can carry N packages.
CREATE OR REPLACE VIEW additional_packages AS
SELECT repo, issue_number,
       unnest(regexp_extract_all(body, 'AdditionalPackage:\s*(\S+)', 1)) AS source_url
FROM comments
WHERE body LIKE '%AdditionalPackage%';
"""


def connect(base: str = "data") -> duckdb.DuckDBPyConnection:
    """A DuckDB connection with the issues/comments/events views registered."""
    con = duckdb.connect()
    con.execute(VIEWS.format(base=base))  # runs all CREATE VIEW statements
    return con
