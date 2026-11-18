# AGENTS.md

Instructions for coding agents working in this repo. Human contributors: see CONTRIBUTING.md.

## Co-review agent: review standards

The co-review agent (`app/src/agent.ts` RULES, `app/skills/*.md`) drafts reviews that the Bioconductor
core team reads. Keep these standards in the prompts whenever you edit them, and check new drafts
against them. Source: core-team feedback on a posted review, adopted 2026-11-18 (#64, #65, PRs #66, #67).

- **Never soften Bioconductor standards.** Anything the guidelines or the core team require is written
  as **Required:**, never "consider", "suggested" or a question, and is never traded away to get a
  package accepted. Don't make drafts stricter than the standard either.
- **Bioconductor data containers.**
  - Packages must accept the appropriate Bioconductor class (SummarizedExperiment / SingleCellExperiment;
    GRanges, MultiAssayExperiment, SpatialExperiment etc. where they fit). Seurat-only (or AnnData, or
    plain matrices standing in for assay data) does not meet the standard.
  - Functions that transform or annotate the data in the container (normalization, filtering, QC
    metrics, cell/feature labels, imputation, reduced dimensions, new assays) must return the same class
    they were given, with the result stored in it. Converting to Seurat internally and returning Seurat
    or a list does not count.
  - Functions that compute analysis results (differential expression tables, test statistics,
    enrichment/association results) may return a data.frame or DataFrame. Don't require these to be
    stored back in the input object.
  - The vignette's default examples use the Bioconductor classes and show the package in a Bioconductor
    workflow; other ecosystems can be secondary.
- **Comparison with existing packages** belongs in the submitter's vignette (introduction, comparison,
  justification). The first review requires it if missing and reacts to it; it doesn't write its own
  comparison. Asking for it at submission time is a BiocContributions process change (#20).
- **First review shape:** open with a 4–6 sentence summary of what the package does and how it is built,
  and answer submitter comments that no reviewer has answered yet.

## Don't touch reviews on GitHub

Agents must not change existing reviews or add new reviews (comments) on
`Bioconductor/BiocContributions`. Test skills and prompts without posting: run them locally
(`cd app && bun run dev`) or against the API, and read the draft; never post a draft.
