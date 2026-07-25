# Design

## Principle

The Bioconductor pipeline is already ~60% mechanized (`BiocCheck` + `R CMD
check` + the Single Package Builder). **Don't have an LLM re-derive what a
deterministic tool already computes.** Split every check into:

- **Deterministic** — pass/fail a tool emits. Parse it, never re-reason it.
- **Judgment** — appropriateness, reuse of core infra, API design, doc/vignette
  quality, redundancy with existing packages. This is the LLM's only job.

Everything advisory: bots post draft comments a human approves. No autonomous
label/accept/decline (bioc-issue-bot already owns the deterministic labels, and
review is a *relationship* with the submitter).

## Multi-agent review process

A submission fans out to specialized agents, each producing structured findings,
then a synthesis agent writes the checklist-shaped draft review. Most agents are
**deterministic extractors** feeding a thin LLM layer — the LLM judges, it
doesn't measure.

| Agent | Kind | Produces |
|---|---|---|
| **static-check** | deterministic | `BiocCheckGitClone()` + `BiocCheck(new-package=TRUE)` + `R CMD check` output, parsed to `{errors[], warnings[], notes[], build_status}`. Reuse SPB reports where they exist. |
| **stats** | deterministic | LOC, # functions, # exported objects, # man pages w/ runnable examples, # unit tests, dependency count, vignette count/eval-ratio, package size. |
| **classes-and-methods** | deterministic → LLM | Extract: S4 classes / generics / methods **introduced** vs core-infra classes **used** (`SummarizedExperiment`, `GRanges`, `Biostrings`, `BiocParallel`, `BiocFileCache`, `Experiment/AnnotationHub`). LLM judges: does it reinvent infra it should reuse? |
| **social-coding** | deterministic | Signals from the submitter's GitHub repo: commit history/cadence, README, CI, tests, license, issue responsiveness, contributor count. Cheap via `gh api`. |
| **precedent** (retrieval) | deterministic | Top-k past reviews of packages with overlapping biocViews/deps/description + their outcomes; existing packages with overlapping functionality (redundancy check). |
| **synthesis** | LLM | Consumes all of the above; emits the reviewer-checklist-structured advisory draft, each item pass/concern/blocker + cited rationale. Deterministic findings are authoritative — the LLM may not soften a BiocCheck ERROR. |

Grounding for the LLM: (i) `precedent` retrieval as context + a small pinned set
of exemplary past reviews for tone/format; (ii) **tool access to the cloned
repo** (read_file/grep) — targeted reads, not tarball-stuffing; (iii) the parsed
deterministic results, marked authoritative. Backend: Claude API tool-use;
prompt-cache the static system prompt + guideline reference + exemplars (the
dominant cost lever at volume).

The fan-out maps onto the `Workflow` tool (finders in parallel → synthesis),
but a single tool-use call is fine for v1 — reach for the agent loop only when
it demonstrably falls short.

## Contribution-manager bot

Mostly deterministic signal extraction from the timeline DB + light LLM
narration. Stale detection (vs the 2–3 wk reviewer / 3–4 wk submitter norms),
state-machine position (blocking party = submitter/reviewer/bot), reviewer load
+ topic-match routing, round-trip/friction count. LLM only for one-line status
summaries, nudge wording, and a routing justification. Dashboard = DB view +
template, no LLM.

## Build order

1. **DB** — done (`fetch.sh`, `views.sql`). Add per-submission DESCRIPTION,
   biocViews, deps, outcome; embeddings on description+biocViews.
2. **static-check + stats harness** — independently valuable, zero LLM risk.
3. **precedent retrieval** — biocView filter + vector rank. ~80% of the value.
4. **synthesis LLM layer** — advisory draft, human-approved.
5. **manager bot** — queries + board + optional narration.

### Laziest useful MVP

A read-only bot that on a new submission posts **one comment**: the parsed
BiocCheck/SPB findings in human-readable form + a precedent section ("3 similar
past packages and how their reviews went, with links"). Steps 1–3, no LLM
judgment, no autonomy — impossible to be wrong in a damaging way, and it kills
the two most tedious parts of the 30–90 min human review (the mechanical scan
and the "have we seen this before" lookup). Add the LLM layer only once
reviewers confirm the precedents land.

## What real review threads taught us (corrections to the research)

Read 9 real issues across outcomes (#4218/#4228 accepted, #3332 contested-accept,
#3734/#3909 declined, #3944/#4014/#3735 inactive, #3224 pending). Key deltas:

- **Review is two-phase, and the first phase is the core team, not the assigned
  reviewer.** Heavy technical back-and-forth (reject non-CRAN/Bioc deps, demand
  interop, challenge biocViews, demand real tests) happens during *moderation*
  while the issue is still `1. awaiting moderation` — done by core (lshep,
  LiNk-NY). Many packages are declined or die here and never reach a formal
  reviewer. `3d. needs interop` / `3e. pending pre-review changes` are applied
  by the moderator in this phase. **Design impact:** the reviewer bot's biggest
  value is at *pre-review*, and "actor role" (core-team vs assigned-reviewer vs
  community vs bot) is the single most important signal to model — don't collapse
  everyone into "reviewer".
- **Declined ≠ inactive.** Decline is a hard, affirmative editorial "no" (usually
  first review), citing redundancy / lack of interop / lack of novelty — the
  package often *passes* R CMD check when declined. Inactive is abandonment: 1–2
  nudges, then the bot auto-closes. The `(inactive)` title prefix is applied to
  both, so **title is not a reliable outcome signal — use the `3b`/`3c` label.**
- **There is no single review checklist.** Format is per-reviewer: real
  task-lists keyed to BiocCheck, two-bullet free-form, long prose with embedded
  reprex + `sessionInfo()`, or section-by-section. The `label` events — not the
  comment text — are the reliable state machine.
- **Latency norms are months, not 2–3 weeks** (inactive closures at ~4 months;
  reviewers post OOO notices; "2–3 weeks" is an aspiration routinely missed).
  The manager bot's stale thresholds must reflect this.
- **Bot mechanics the research got wrong:** builds are triggered by a *version
  bump pushed to git.bioconductor.org*, not a GitHub push; there are **no slash
  commands** in the legacy repo (re-review = submitter comments, human flips the
  label); build states include `ABNORMAL`/`TIMEOUT`/`skipped` and combinations;
  the magic string **`AdditionalPackage: <URL>`** bundles N packages into one
  issue (so model **1 issue → N packages**, not 1:1); the pre-push hook rejects
  git-conflict-marker patterns and false-positives on `message(">>>>>>")`.

**Concrete ingest additions this implies** (all present in the timeline we
already fetch — surface them in views/parsers):
- `labeled`/`unlabeled` events → the authoritative state machine (already in `events`).
- `assigned`/`unassigned` events → reviewer identity, distinct from the label and
  the bot's "reviewer assigned" comment (capture all three; they don't co-occur).
- `renamed` events (the `(inactive)` prefix), `cross-referenced` events (links to
  the `AdditionalPackage` sibling issues / other repos).
- Parse bot comments for commit SHA (`starting a build for commit id:`), build
  state, `buildreport` URL, and per-version tarball name → the full version-bump
  OK/WARN/ERROR trajectory, otherwise invisible.
- Per-comment `reactions.total_count` and `updated_at != created_at` (edited).
- Derive `actor_role` for every actor. Model `issue 1 → N packages`.
- DESCRIPTION is posted by the bot exactly once (parse it for initial biocViews /
  deps / license / version); its diff over time lives in git.bioconductor.org, not
  the thread.

## Reference facts to pull when building

- `docs/package-review-checklist.md` in `Bioconductor/Contributions` — the exact
  reviewer checklist; use as the synthesis agent's output schema.
- BiocCheck rule set: https://bioconductor.org/packages/release/bioc/vignettes/BiocCheck/inst/doc/BiocCheck.html
- Guidelines: https://contributions.bioconductor.org/ (general, r-code,
  review-expectation ch.28, reviewtools ch.29).
