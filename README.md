# bioc-contrib-intelligence

Database + bot toolkit for the Bioconductor package-submission review process.

## Data

Two trackers are ingested (both, because they overlap during a live migration):

| Repo | Role | Size |
|---|---|---|
| `Bioconductor/Contributions` | legacy tracker, historical corpus (2016–2025) | ~4,300 closed issues |
| `Bioconductor/BiocContributions` | new tracker (R-universe / GitHub Actions) | ~113 issues, live |

For each repo we store **all** issues (open + closed) plus the **per-issue
timeline** (comments *and* label/assign/close/cross-reference events in one
stream) as append-only JSONL under `data/<repo>/`. JSONL is the source of truth;
DuckDB reads it directly — no import step.

> We fetch per-issue timelines rather than the repo-wide `issues/comments` and
> `issues/events` endpoints because GitHub hard-caps those at 30k items
> (page 300 → HTTP 422), which silently truncates the legacy repo.

## Install & run

Uses [uv](https://docs.astral.sh/uv/). Auth via `GITHUB_TOKEN`/`GH_TOKEN` or a
logged-in `gh`.

```bash
uv sync                                   # create venv, install deps
uv run bcintel fetch                       # backfill both repos -> data/*/*.jsonl
uv run bcintel fetch --repo Bioconductor/BiocContributions --limit 5   # small test
uv run bcintel sql "SELECT state, count(*) FROM issues GROUP BY 1"
```

`fetch` is a single-writer async producer/consumer: httpx producers pull issue
timelines concurrently (bounded by `--concurrency`, default 10), one consumer
owns every write, and tenacity handles retries + rate limits. Resumable — re-run
to continue or refresh.

Views (`bcintel.db`): `issues`, `comments`, `events` — projected and deduped
over the raw JSONL. `events` reconstructs the label/assignment/close history the
plain issues endpoint drops.

## Dashboard

`report.qmd` is a living dashboard — the lifecycle figure
(`figures/lifecycle.dot` via quarto-livefigures) plus summary tables computed
live from the JSONL on every render:

```bash
quarto add seandavi/quarto-livefigures   # one-time: installs the figure extension
uv run quarto render report.qmd          # -> report.html
```

## Reviewing submissions

```bash
uv run bcintel bot                 # lightweight triage briefing per open issue (metadata)
uv run bcintel review --patch      # clone each changed submission, static review + draft PR
uv run bcintel cycle               # one tick: fetch, then rebuild the dashboard (no review)
```

`review` is off the timer: package review is on hold, and its build
parsing doesn't yet read the new tracker's r-universe results. The dashboard
writes a placeholder `i/<n>.review.md` ("REVIEW BODY HERE") per open issue for
the app to build against.

`review` is idempotent (keyed on the cloned HEAD sha), so it only acts
on submissions that changed. Output is dry-run Markdown under `bot_out/<repo>/`:
`issue-<n>.md` (review comment) and `issue-<n>.pr.md` (proposed safe-fix PR).
Needs `GOOGLE_API_KEY` (or `ANTHROPIC_API_KEY`) for the judgment layer.

**Scheduling:** a systemd user timer (`scripts/systemd/`) runs
`scripts/run-cycle.sh` every 5 min (legacy tracker once a day). `.github/workflows/reactive-review.yml` is
disabled.

## Dev

```bash
uv run ruff check src tests
uv run pytest -q
```

## Roadmap

Build order (see `DESIGN.md`): **DB** (this) → deterministic check harness →
retrieval over past reviews → multi-agent review → contribution-manager bot.
Downstream: dashboards, an advisory reviewer bot, a triage/manager bot.
