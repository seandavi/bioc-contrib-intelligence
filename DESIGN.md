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

## Reference facts to pull when building

- `docs/package-review-checklist.md` in `Bioconductor/Contributions` — the exact
  reviewer checklist; use as the synthesis agent's output schema.
- BiocCheck rule set: https://bioconductor.org/packages/release/bioc/vignettes/BiocCheck/inst/doc/BiocCheck.html
- Guidelines: https://contributions.bioconductor.org/ (general, r-code,
  review-expectation ch.28, reviewtools ch.29).
