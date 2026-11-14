---
label: First review
description: A full first review against the Bioconductor package guidelines, with code citations.
model: claude-opus-5-5
---
Draft a full first review.

Work through the package before writing: DESCRIPTION, NAMESPACE, R/ (structure, reuse of Bioconductor classes such as SummarizedExperiment/SingleCellExperiment/GRanges vs reinventing them, vectorisation, sapply/1:n/T/F, error handling, long functions), man/ (examples runnable, \value present, dontrun use), vignettes/ (installation from Bioconductor, evaluates real code, narrative), tests/, inst/, data and file sizes, and the current check findings (get_check_log for bioc-checks).
Use search_code to find patterns across files rather than reading everything.

Write the review into the draft (write_draft) in the usual Bioconductor review shape:
- a short opening (thanks; one-line summary of the package),
- sections `## General`, `## DESCRIPTION`, `## NAMESPACE`, `## Vignette`, `## Man pages`, `## R code`, `## Unit tests` (omit empty ones),
- each point a checkbox `- [ ]`, specific and actionable, citing code as `[R/file.R#L10-L20](permalink)`; mark required vs suggested (`**Required:**` / `Suggested:`),
- a closing line on next steps (push a version bump, then comment).
In chat, give a 5-line summary of the most important issues.
