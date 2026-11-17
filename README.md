# bioc-contrib-intelligence

[![test](https://github.com/seandavi/bioc-contrib-intelligence/actions/workflows/test.yml/badge.svg)](https://github.com/seandavi/bioc-contrib-intelligence/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Code of Conduct](https://img.shields.io/badge/Code%20of%20Conduct-Bioconductor-brightgreen)](CODE_OF_CONDUCT.md)

Review-queue intelligence for Bioconductor package submissions: who owes the
next move on each review, how long it has been waiting, what the checks say now,
and a co-review assistant that helps reviewers write the next comment.

**App:** <https://reviewer.bioconductor.org>. Signed out, it shows tracker-wide
counts and a reviewer guide. Signing in with GitHub gives reviewers with open
assignments on
[Bioconductor/BiocContributions](https://github.com/Bioconductor/BiocContributions)
their queue, and the triage team the overview.

## Why

A submission's status is spread across the issue thread, issue labels, the
r-universe staging build and the review bot's state. Labels collect over time,
and r-universe re-runs checks without posting to the issue, so submitters and
reviewers often don't have the full picture. This project derives each
submission's current state from those sources and shows it in one place.
Live counts: [`/api/public/summary`](https://reviewer.bioconductor.org/api/public/summary).
Background: [`docs/specs/reviewer-app.md`](docs/specs/reviewer-app.md).

## What's here

| Part | What it does | Where |
|---|---|---|
| **Corpus** | Every issue and its full timeline from both trackers, as append-only JSONL; DuckDB views read it directly. | `src/bcintel/fetch.py`, `db.py` |
| **Derived state** | Whose move and since when, parsed build reports and versions, outcomes, live r-universe results. | `db.py`, `dashboard.py` |
| **Snapshot** | `data.json` plus a file per issue, rebuilt every 5 min and synced to R2. | `dashboard.py`, `scripts/run-cycle.sh` |
| **Reviewer app** | Cloudflare Worker (Hono) + React: My queue, Overview, Review detail, guide, usage. | [`app/`](app/README.md) |
| **Co-review agent** | Chat sidebar and a shared draft on Review detail. Reads the thread, live checks, logs and source at the built commit; edits only the reviewer's draft. Skills: First review, Follow-up, Check triage, Fit & overlap, License & provenance, Nudge. | `app/src/agent.ts`, `app/skills/` |
| **Research** | Lifecycle state machine, comment signals (Cloudflare Clef), the past-review corpus behind the skills, cost log. | `STATE_MACHINE.md`, `experiments/`, [`docs/writeups/`](docs/writeups/2026-11-co-review-corpus.md) |

```
GitHub (both trackers) ─┐
r-universe biocstaging ─┴─> bcintel cycle (every 5 min) ─> data/*.jsonl ─> DuckDB views
                                                          └─> snapshot ─> R2 ─> Worker ─> app / API
                                 Worker ─> AI Gateway (co-review), GitHub + r-universe (logs, source)
```

## Data

| Tracker | Role |
|---|---|
| `Bioconductor/BiocContributions` | current tracker (r-universe builds, GitHub Actions bot); refreshed every 5 min |
| `Bioconductor/Contributions` | legacy tracker (2016–2025), about 4,300 issues; history and the past-review corpus; refreshed daily |

Everything comes from public GitHub and r-universe data. `data/` isn't in git;
`bcintel fetch` rebuilds it and the tick backs it up to R2. We fetch per-issue
timelines because GitHub caps the repo-wide comment and event endpoints at 30k
items, which would truncate the legacy tracker.

## Run it

Pipeline: Python with [uv](https://docs.astral.sh/uv/); GitHub auth from
`GITHUB_TOKEN`, `GH_TOKEN` or a logged-in `gh`.

```bash
uv sync
uv run bcintel fetch                                   # both trackers -> data/*/*.jsonl
uv run bcintel sql "SELECT * FROM reviewer_queue LIMIT 5"
uv run bcintel cycle                                   # fetch + r-universe + rebuild the snapshot
uv run ruff check src tests && uv run pytest -q
```

Main views: `issues`, `comments`, `events`, `activity`, `reviewer_queue`,
`build_reports`, `checks`, `packages`. A systemd user timer
(`scripts/systemd/`) runs `scripts/run-cycle.sh` every 5 minutes.

App (bun, wrangler), including auth, API routes and the agent's setup:
[`app/README.md`](app/README.md).

## Status

| Live | Not yet |
|---|---|
| Queue, Overview, Review detail, live r-universe checks | Posting comments and (re)assigning from the app ([#8](https://github.com/seandavi/bioc-contrib-intelligence/issues/8)) |
| Co-review agent and skills (experimental; drafts only, nothing is posted) | MCP server ([#9](https://github.com/seandavi/bioc-contrib-intelligence/issues/9)) |
| Public landing page, guide and summary API | Scheduled comment signals ([#10](https://github.com/seandavi/bioc-contrib-intelligence/issues/10)), webhook freshness ([#11](https://github.com/seandavi/bioc-contrib-intelligence/issues/11)) |

Tracking: app [#13](https://github.com/seandavi/bioc-contrib-intelligence/issues/13),
co-review agent [#39](https://github.com/seandavi/bioc-contrib-intelligence/issues/39)
and its discussion [#53](https://github.com/seandavi/bioc-contrib-intelligence/issues/53),
observations and recommendations about the contributions process to discuss with
the Bioconductor core team [#20](https://github.com/seandavi/bioc-contrib-intelligence/issues/20).

Scope: the co-review agent is a writing aid for a human reviewer, who decides
what gets posted. Automated package review is
[BiocPkgReviewer](https://github.com/Bioconductor/BiocPkgReviewer)'s job. The
earlier batch-review experiments (`bcintel review`, `bot`, `gate1*`, `DESIGN.md`)
are kept but not scheduled.

## Contributing, license, citation

See [CONTRIBUTING.md](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md).
Report security issues privately ([SECURITY.md](SECURITY.md)). MIT licensed
([LICENSE](LICENSE)); cite with [CITATION.cff](CITATION.cff).
