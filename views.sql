-- DuckDB views over the raw JSONL. No import step — query the files directly.
--   duckdb -init views.sql            (interactive)
--   duckdb -init views.sql -c "SELECT state, count(*) FROM issues GROUP BY 1"
-- union_by_name tolerates the two repos having slightly different JSON shapes.
-- comments and events are both derived from the per-issue timeline stream.

CREATE OR REPLACE VIEW issues_raw   AS SELECT * FROM read_json_auto('data/*/issues.jsonl',   union_by_name=true);
CREATE OR REPLACE VIEW timeline_raw AS SELECT * FROM read_json_auto('data/*/timeline.jsonl', union_by_name=true);

-- Issues — projected, deduped (a refetch appends duplicate rows keyed by number).
CREATE OR REPLACE VIEW issues AS
SELECT _repo AS repo, number, title, state, state_reason,
       user.login AS author, created_at, updated_at, closed_at,
       [l.name FOR l IN labels] AS labels,
       [a.login FOR a IN assignees] AS assignees,
       comments AS comment_count, body
FROM issues_raw
QUALIFY row_number() OVER (PARTITION BY _repo, number ORDER BY updated_at DESC) = 1;

-- Comments — the 'commented' timeline events.
CREATE OR REPLACE VIEW comments AS
SELECT _repo AS repo, _issue AS issue_number, id,
       user.login AS author, author_association, created_at, updated_at,
       user.login IN ('bioc-issue-bot','github-actions[bot]') AS is_bot, body
FROM timeline_raw
WHERE event = 'commented'
QUALIFY row_number() OVER (PARTITION BY id ORDER BY updated_at DESC) = 1;

-- Events — the full timeline (labeled/unlabeled/assigned/closed/cross-referenced/…).
-- Note: label events carry .actor; commented events carry .user — coalesce.
CREATE OR REPLACE VIEW events AS
SELECT _repo AS repo, _issue AS issue_number, id, event,
       coalesce(actor.login, user.login) AS actor,
       label.name AS label, assignee.login AS assignee, created_at
FROM timeline_raw
QUALIFY row_number() OVER (PARTITION BY _issue, event, coalesce(id, 0), coalesce(created_at, '') ORDER BY created_at DESC) = 1;
