# ADR 0001: The co-review agent holds Bioconductor standards, scoped to what they require

Status: accepted, 2026-11-18. Issues #64, #65; PRs #66, #67. Operating rules: `AGENTS.md`.

## Context

A first review drafted with the co-review agent and posted on a Seurat-only package asked the
submitter to accept a SingleCellExperiment and to *consider* returning Bioconductor objects. A core
team member pointed out that this reads as optional, while the standard is not: packages must work
with SummarizedExperiment / SingleCellExperiment and fit into Bioconductor workflows, and the vignette's
default examples must show that. She also asked that the vignette carry an introduction comparing
the package with existing ones, as Levi Waldron's review tool prompts for.

The first fix over-corrected: drafts began requiring every result, including differential expression
tables, to be stored back in the input SummarizedExperiment. That isn't a Bioconductor requirement.

## Decision

1. Requirements are written as **Required:** and never softened or traded for acceptance; drafts are
   also not made stricter than the standard.
2. Accepting the appropriate Bioconductor container is required. Functions that transform or annotate
   the data must return the container they were given; analysis results may be data.frames or
   DataFrames. Vignette examples use the Bioconductor classes.
3. The comparison with existing packages is the submitter's job, in the vignette. The first review
   requires it when missing and reacts to it; the agent doesn't write its own comparison. Requiring it
   at submission time would be a BiocContributions process change (recorded on #20, not filed upstream).
4. First reviews open with a 4–6 sentence summary of what the package does and how it is built, and
   answer submitter comments that no reviewer has answered.
5. The rules live in the agent's base rules (`app/src/agent.ts`), so they apply to every skill and to
   free chat, not only to First review.

## Consequences

Drafts state container requirements per function (what class goes in, what must come out), which is
more useful to submitters and matches what the core team enforces. The classification of each function
as transform vs analysis result is a model judgement; reviewers should check it. Changes to these rules
need a new ADR or an amendment here, and AGENTS.md updated to match.
