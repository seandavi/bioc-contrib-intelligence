# Submission lifecycle — the derived state machine

This is not a hand-drawn guess; it's **derived from the `labeled` events** of all
4,344 legacy-tracker issues (`label_transitions` view). Edge counts below are
observed transition frequencies. Regenerate anytime:

```sql
-- the edges of the machine (stage labels only), with counts
WITH s AS (
  SELECT issue_number, to_label, from_label
  FROM label_transitions
  WHERE repo LIKE '%/Contributions' AND coalesce(from_label, to_label) IN (
    '1. awaiting moderation','pre-check passed','pre-review','2. review in progress',
    '3a. accepted','3b. declined','3c. inactive','3d. needs interop','3e. pending pre-review changes')
)
SELECT coalesce(from_label,'(start)') AS src, to_label AS dst, count(*) n
FROM s GROUP BY 1,2 HAVING n >= 5 ORDER BY n DESC;
```

## The two phases

The single biggest correction from reading real threads, now confirmed in the
data: **substantive review happens in two phases, and the first is the core
team, not the assigned reviewer.**

- **Phase 1 · Moderation** (`1. awaiting moderation` → `pre-check passed` →
  `pre-review`, with side-states `3e. pending pre-review changes` and
  `3d. needs interop`). Driven by core team: `pre-check passed` is applied by
  `lshep` (542×) and `vjcitn` (327×). Many packages are held, sent back, or
  declined here and never reach a formal reviewer.
- **Phase 2 · Review** (`2. review in progress` → `3a`/`3b`/`3c`). The
  `2. review in progress` label is applied by `bioc-issue-bot` (643×) and
  `lshep` (501×); `3a. accepted` is finalized by core (`lshep` 118×,
  `LiNk-NY` 114×); the rare `3b. declined` is applied by community reviewers
  (`PeteHaitch`, `DarioS`).

## States

| State | Kind | Meaning |
|---|---|---|
| `(start)` | initial | issue opened by contributor |
| `1. awaiting moderation` | phase 1 | bot posted DESCRIPTION; core team triaging |
| `3e. pending pre-review changes` | phase 1 hold | core asked for fixes; loops back |
| `3d. needs interop` | phase 1 hold | must integrate with core Bioc classes |
| `pre-check passed` | phase 1 | passed moderation; added to git.bioconductor.org |
| `pre-review` | phase 1 | build clean, awaiting reviewer assignment |
| `2. review in progress` | phase 2 | reviewer assigned; active review |
| `3a. accepted` | terminal ✓ | accepted → nightly builds; issue closed |
| `3b. declined` | terminal ✗ | hard editorial reject (redundancy/interop/novelty) |
| `3c. inactive` | terminal ✗ | abandoned; bot auto-closes after silence |

## Key transitions (observed counts)

| From | To | n | Note |
|---|---|---:|---|
| `(start)` | `1. awaiting moderation` | 1167 | every submission |
| `1. awaiting moderation` | `pre-check passed` | 536 | happy path |
| `1. awaiting moderation` | `3e. pending pre-review changes` | 308 | sent back at moderation |
| `1. awaiting moderation` | `2. review in progress` | 262 | **skips pre-check/pre-review** |
| `1. awaiting moderation` | `3d. needs interop` | 55 | interop demanded early |
| `3e. pending pre-review changes` | `pre-check passed` | 251 | **loop** after resubmit |
| `pre-check passed` | `pre-review` | 493 | happy path |
| `pre-check passed` | `2. review in progress` | 314 | **skips pre-review** |
| `pre-review` | `2. review in progress` | 465 | happy path |
| `2. review in progress` | `3a. accepted` | 837 | the dominant outcome |
| `2. review in progress` | `3c. inactive` | 118 | stalls in review |
| `2. review in progress` | `3d. needs interop` | 10 | |

Note the machine is **not** a clean linear pipeline: there are legitimate
skip-edges (moderation straight to review), a resubmit loop
(`pending → pre-check`), and backward edges (relabel to `awaiting moderation`).
Terminal states all close the issue; `3c. inactive` is closed by the bot on
timeout, the others by a human.

## How this drives the bots

- **Reviewer bot**: highest value at **Phase 1** — it's where core team spends
  effort on interop / redundancy / test-quality judgment (see `DESIGN.md`). Gate
  its advice on the current state: pre-`pre-review` → focus on the moderation
  checklist; `2. review in progress` → focus on the deep review.
- **Manager bot**: the machine + timestamps give exact "blocking party" and
  dwell time per state. Stale thresholds must reflect real cadence (inactive
  closures at ~4 months, not weeks). `3e. pending`/`3d. interop` dwell = waiting
  on submitter; `pre-review` dwell = waiting on reviewer assignment.
- **`actor_role`** on every label event is the load-bearing signal — the same
  label means different things applied by bot vs core vs community reviewer.

## Figure

`figures/lifecycle.dot` is the version-controlled source, rendered by
[quarto-livefigures](https://github.com/seandavi/quarto-livefigures) — reference
it from a `.qmd` (`![Lifecycle](figures/lifecycle.dot){#fig-lc}`) or render
directly with `dot -Tsvg figures/lifecycle.dot`. The edge counts in the `.dot`
come from the `label_transitions` query above, so the figure regenerates from
data rather than drifting.
