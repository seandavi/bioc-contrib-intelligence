-- DuckDB views over the raw JSONL. No import step — query the files directly.
--   duckdb -init views.sql            (interactive)
--   duckdb -init views.sql -c "SELECT state, count(*) FROM issues GROUP BY 1"
-- union_by_name tolerates the two repos having slightly different JSON shapes.

CREATE OR REPLACE VIEW issues_raw   AS SELECT * FROM read_json_auto('data/*/issues.jsonl',   union_by_name=true);
CREATE OR REPLACE VIEW comments_raw AS SELECT * FROM read_json_auto('data/*/comments.jsonl', union_by_name=true);
CREATE OR REPLACE VIEW events_raw   AS SELECT * FROM read_json_auto('data/*/events.jsonl',   union_by_name=true);

-- Projected, deduped (a full refetch appends duplicate rows keyed by id/number).
CREATE OR REPLACE VIEW issues AS
SELECT _repo AS repo, number, title, state, state_reason,
       user.login AS author, created_at, updated_at, closed_at,
       [l.name FOR l IN labels] AS labels,
       [a.login FOR a IN assignees] AS assignees,
       comments AS comment_count, body
FROM issues_raw
QUALIFY row_number() OVER (PARTITION BY _repo, number ORDER BY updated_at DESC) = 1;

CREATE OR REPLACE VIEW comments AS
SELECT _repo AS repo,
       CAST(regexp_extract(issue_url, '(\d+)$', 1) AS BIGINT) AS issue_number,
       id, user.login AS author, author_association, created_at, updated_at,
       user.login IN ('bioc-issue-bot','github-actions[bot]') AS is_bot, body
FROM comments_raw
QUALIFY row_number() OVER (PARTITION BY id ORDER BY updated_at DESC) = 1;

CREATE OR REPLACE VIEW events AS
SELECT _repo AS repo, issue.number AS issue_number, id, event,
       actor.login AS actor, label.name AS label, assignee.login AS assignee, created_at
FROM events_raw
QUALIFY row_number() OVER (PARTITION BY id ORDER BY created_at DESC) = 1;
