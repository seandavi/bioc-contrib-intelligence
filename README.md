# bioc-contrib-intelligence

Review-queue intelligence for Bioconductor package submissions: who owes the
next move on each review, how long it has been waiting, and what changed since
the last comment.

**App:** <https://bioc-reviews.seandavi.workers.dev> (sign in with GitHub; for
reviewers with open assignments on
[Bioconductor/BiocContributions](https://github.com/Bioconductor/BiocContributions)
and its triage team).

## Why

Submitters and reviewers often don't have the full picture of a review. A
submission's status is spread across the issue thread, issue labels, the
r-universe staging build and the review bot's state. Labels collect over time,
and r-universe re-runs checks without posting to the issue. On 2026-11-02, 48 of
the 120 open reviewer assignments had been the reviewer's move for more than four
weeks.

This project derives each submission's current state from those sources and
shows it to reviewers and the core team in one place. Background and numbers:
[`docs/specs/reviewer-app.md`](docs/specs/reviewer-app.md).

## What's here

| Part | What it does | Where |
|---|---|---|
| **Corpus** | Fetches every issue and its full timeline from both trackers into append-only JSONL. DuckDB views read it directly. | `src/bcintel/fetch.py`, `db.py` |
| **Derived state** | Whose move it is and since when, parsed build reports and versions, outcomes, live r-universe check results. | `db.py`, `dashboard.py` |
| **Snapshot** | `data.json` plus a file per issue, rebuilt every 5 min and synced to R2. | `dashboard.py`, `scripts/run-cycle.sh` |
| **Reviewer app** | Cloudflare Worker (Hono API) with a React UI: My queue, Overview, Review detail, AI review editor. | [`app/`](app/README.md) |
| **Research** | Lifecycle state machine, comment-signal labelling (Cloudflare Clef), cost log. | `STATE_MACHINE.md`, `experiments/` |

```
GitHub (both trackers) ─┐
r-universe biocstaging ─┼─> bcintel cycle (every 5 min, onclappc02) ─> data/*.jsonl ─> DuckDB views
                        │                                               └─> snapshot ─> R2 ─> Worker ─> app / API
```

## Data

| Tracker | Role |
|---|---|
| `Bioconductor/BiocContributions` | current tracker (r-universe builds, GitHub Actions bot); refreshed every 5 min |
| `Bioconductor/Contributions` | legacy tracker (2016–2025), about 4,300 issues; history and calibration; refreshed daily |

Everything comes from public GitHub and r-universe data. The corpus isn't in
git (`data/` is ignored); it is rebuilt by `bcintel fetch` and backed up to R2.

We fetch per-issue timelines rather than the repo-wide comments and events
endpoints, because GitHub caps those at 30k items, which would truncate the
legacy tracker.

## Run it

Python with [uv](https://docs.astral.sh/uv/); GitHub auth from `GITHUB_TOKEN`,
`GH_TOKEN` or a logged-in `gh`.

```bash
uv sync
uv run bcintel fetch                                   # both trackers -> data/*/*.jsonl
uv run bcintel sql "SELECT * FROM reviewer_queue LIMIT 5"
uv run bcintel cycle                                   # fetch + r-universe + rebuild the snapshot
uv run ruff check src tests && uv run pytest -q
```

Main views: `issues`, `comments`, `events`, `activity`, `reviewer_queue` (whose
move, waiting since, what changed), `build_reports` and `checks` (parsed bot
build reports), `packages` (name, source, outcome).

Scheduling: a systemd user timer (`scripts/systemd/`) runs
`scripts/run-cycle.sh` every 5 minutes. The app has its own instructions in
[`app/README.md`](app/README.md).

## Status and tracking

- Plan: [#13](https://github.com/seandavi/bioc-contrib-intelligence/issues/13).
- Observations about the contributions process, and recommendations to discuss
  with the Bioconductor core team:
  [#20](https://github.com/seandavi/bioc-contrib-intelligence/issues/20).
- The AI review panel shows a placeholder until a review engine is chosen
  ([#12](https://github.com/seandavi/bioc-contrib-intelligence/issues/12)).

Scope: this project covers the review queue (state, waits, hand-offs). It doesn't
do automated package review; see Bioconductor's
[BiocPkgReviewer](https://github.com/Bioconductor/BiocPkgReviewer). The earlier
package-review experiments (`bcintel review`, `bot`, `gate1*`, `DESIGN.md`) are
kept but on hold and not scheduled.
