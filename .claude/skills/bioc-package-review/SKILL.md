---
name: bioc-package-review
description: Review a Bioconductor package submission against the official contribution guidelines, given a local checkout of the package repo. Use when reviewing/critiquing a Bioconductor package, running a submission review, or checking a package against Bioconductor standards.
---

# Bioconductor package review (static)

Review a **local checkout** of a contributed package against the official
[Bioconductor Contributions guide](https://contributions.bioconductor.org/) by
**reading and grepping its source** — this skill executes no build tools. Every
item below is drawn from that guide (or the BiocCheck vignette) and cites its
source URL. Do not invent rules; if something isn't here, check the guide.

**Build/platform pass-fail is out of scope.** Whether the package builds and
checks cleanly is produced by Bioconductor's Single Package Builder (SPB) and
posted as the build-report comment on the submission issue. This static skill
does **not** run `R CMD build`/`check` or `BiocCheck`. If an SPB report already
exists on the issue, reference it; otherwise leave build status unassessed.

## How to run

Given a path to a checked-out package (`$PKG`):

### 1. Static inspection pass

Read / grep the source — no command execution:
- `DESCRIPTION` — fields, version, deps, biocViews, license, Authors@R
- `NAMESPACE` — export/import directives
- `R/*.R` — style and syntax patterns (grep for the [static] items below)
- `man/*.Rd` — man pages, `\value`, `\examples`
- `vignettes/` — vignette source, presence, engine; check `inst/doc/` for pre-built products
- `tests/`, `inst/unitTests/`, `tests/testthat/`, `inst/tinytest/` — test presence
- `inst/extdata`, `inst/scripts`, `data/`, `data-raw/` — data handling
- file sizes (source tree, individual files) and stray/undesirable files

### 2. Judgment pass

Walk the `[judgment]` items: read the actual code and reason about
infrastructure reuse, redundancy with existing packages, S4/API design, and
whether the docs/vignette actually teach. This is where you add value beyond
what a linter sees.

### 3. Output a structured review

Key the output to the checklist areas below. For each raised item give:
**pass / concern / blocker**, a one-line rationale, and the guideline URL it
derives from. Reviewers spend 30 min – 1.5 h per package and evaluate
ease-of-use, documentation, code clarity, and interoperability
(<https://contributions.bioconductor.org/review-expectation.html>).

## The criteria checklist

Tags: **[static]** = mechanically checkable by reading/grepping the source;
**[judgment]** = needs reasoning over the code. The `[static]` patterns mirror
the BiocCheck rule set — check them by inspection, not by running BiocCheck.
Rule source: <https://bioconductor.org/packages/release/bioc/vignettes/BiocCheck/inst/doc/BiocCheck.html>

### DESCRIPTION — <https://contributions.bioconductor.org/description.html>
- [static] Version starts `0.99.` for a new submission, `x.y.z` scheme (#description-ver)
- [static] `Authors@R` present, exactly one maintainer (`cre`) with a live email; ORCID in comment (#description-authors)
- [static] Standard open `License` (e.g. GPL-2, Artistic-2.0); not restrictive (#description-license)
- [static] `biocViews` present, ≥2 leaf-node terms from the same category (#description-biocviews)
- [static] No `Remotes` field; all deps from Bioconductor or CRAN
- [static] No pinned `==` package versions
- [static] No `LazyData: TRUE` for large-data packages
- [judgment] `Description` is ≥3 complete sentences describing functionality (#description-description)
- [judgment] Dependencies placed correctly: `Imports` for namespace use, `Depends` reserved & minimal (~≤3), `Suggests` for vignette/tests, `Enhances` for optional
- [judgment] Recommended fields present: `URL`, `BugReports`, `SystemRequirements` where relevant (#description-bugreport)

### NAMESPACE — <https://contributions.bioconductor.org/namespace.html>
- [static] No match-all export (`exportPattern("^[[:alpha:]]+")`) — exports explicit (#exported-functions)
- [static] No leading-`.` exports; exported names use camelCase/underscores, no `.` (S3) (#function-names)
- [judgment] `importFrom()` preferred for selective imports; `import()` only for many symbols or a Bioconductor class needing full inheritance (#imported-functions)

### R code & style — <https://contributions.bioconductor.org/r-code.html>
- [static] `vapply()` not `sapply()` (#code-syntax-and-efficiency)
- [static] `seq_len()`/`seq_along()` not `1:n`
- [static] `TRUE`/`FALSE` not `T`/`F`
- [static] `is(x, "cls")` not `class(x) ==`
- [static] `system2()` not `system()`
- [static] No `set.seed()` in package code; no `browser()`; no `<<-`; no `Sys.setenv()`
- [static] No direct `@` slot access — use accessors
- [static] Assign with `<-` not `=` (except named args)
- [static] Functions not excessively long (BiocCheck flags >50 lines); 4-space indent, lines <80 chars, no commented-out code / TODOs (#coding-style)
- [judgment] Functions small, focused, not deeply nested; reasonable cyclomatic complexity (#function-development, #cyclomatic-complexity)
- [judgment] Pre-allocate then fill; vectorize; hoist invariants out of loops (#robust-and-efficient-r-code)
- [judgment] Messaging: `message()`/`warning()`/`stop()` correct; `cat()`/`print()` only in `show()` methods (#end-user-messages)

### Classes & methods (S4) / infrastructure reuse — <https://contributions.bioconductor.org/reusebioc.html>
- [judgment] Reuses existing classes — `SummarizedExperiment`, `GRanges`/`GRangesList`, `DataFrame`, `*StringSet`, `SingleCellExperiment`, `MultiAssayExperiment`, `RaggedExperiment` — rather than inventing new ones (#commonclass)
- [judgment] Any novel class is justified and discussed with bioc-devel/Slack before introduction (#package-submission-considerations)
- [judgment] Reuses standard importers: `rtracklayer::import`, `VariantAnnotation::readVcf`, `Rsamtools`/`GenomicAlignments`, `Biostrings::readDNAStringSet`, `ShortRead::readFastq`, `Spectra` (#commonimport)
- [judgment] Interoperability demonstrated across the ecosystem (#bioc-common-motivation)

### Data & Hubs — <https://contributions.bioconductor.org/data.html>
- [static] No data downloads at package load time; no external-platform downloads in code (grep for `download.file`, URLs)
- [judgment] Large data hosted via ExperimentHub/AnnotationHub, not shipped/git-lfs (#experiment-data-package, #other-data)
- [judgment] Downloads cached via BiocFileCache or `tools::R_user_dir()`; never writes to home/wd/package dir; `tempdir()` for scratch (#other-data)
- [judgment] `data/` objects documented (`@usage data(...)`) with provenance; raw files in `inst/extdata`, generation scripts in `inst/scripts/` or `data-raw/` (#adding-data-to-existing-package)

### Documentation & vignettes — <https://contributions.bioconductor.org/docs.html>
- [static] At least one vignette source in `vignettes/` (#vignettes)
- [static] No pre-built vignette products / stray intermediate files in `vignettes/` or sources in `inst/doc/` (#rmarkdown-vignettes)
- [static] Man page for every exported function/class; runnable `\examples`; non-empty `\value`; no canned boilerplate (#man-pages)
- [judgment] Vignette is evaluated (not static); code chunks actually run — `eval=FALSE`/`dontrun`/`donttest` justified, not pervasive (#vignettes)
- [judgment] Vignette has Intro/abstract explaining objectives, why it belongs in Bioconductor, comparison to related packages; actually teaches usage (#vignettes)
- [judgment] Uses `BiocStyle` output; installation chunks `eval=FALSE`; `sessionInfo()` at end (#rmarkdown-vignettes)
- [judgment] References to methods and related packages included (#doc-require)

### Unit tests — <https://contributions.bioconductor.org/tests.html>
- [static] Test framework wired: tests in `tests/testthat/`, `inst/unitTests/`, or `inst/tinytest/` with matching `tests/*.R` runner + `Suggests` entry (#tests)
- [judgment] Tests present and meaningful, covering key functionality; avoid `skip_on_bioc()` masking; reasonable coverage (#test-coverage)

### Versioning / size / files — <https://contributions.bioconductor.org/versionnum.html>
- [static] Version `0.99.z`, `x.y.z` (#new-packages)
- [static] Source package < 10 MB; individual files ≤ 5 MB (general.html #package-size, #individual-file-size)
- [static] No undesirable files (`.DS_Store`, `.git`, `*.Rproj`, `*.so`, ...) (general.html #undesirable-files)

### Appropriateness & redundancy — <https://contributions.bioconductor.org/reusebioc.html>, <https://contributions.bioconductor.org/review-expectation.html>
- [judgment] Provides genuinely new functionality, not a re-implementation of an existing Bioconductor/CRAN package
- [judgment] API design clean and idiomatic; package easy to use
- [judgment] Scope fits Bioconductor (genomics/high-throughput biology)

## Static vs judgment

The `[static]` items are mechanically checkable by reading/grepping the source
and mirror the BiocCheck rule catalog — but this skill checks them **by
inspection, never by running BiocCheck**. Authoritative build/BiocCheck
pass-fail comes from the SPB build report on the submission issue, if present.
Your added value is the **[judgment]** items no linter sees: infrastructure
reuse, redundancy vs existing packages, class/API design, whether the vignette
and docs actually teach, data-handling patterns, and overall appropriateness.

For the exact named rules behind the `[static]` patterns, see the BiocCheck
vignette:
<https://bioconductor.org/packages/release/bioc/vignettes/BiocCheck/inst/doc/BiocCheck.html>

## References

- Contributions guide home / TOC — <https://contributions.bioconductor.org/>
- General development & correctness — <https://contributions.bioconductor.org/general.html>
- Build / Check / BiocCheck — <https://contributions.bioconductor.org/build-check-bioccheck.html>
- DESCRIPTION — <https://contributions.bioconductor.org/description.html>
- NAMESPACE — <https://contributions.bioconductor.org/namespace.html>
- R code & style — <https://contributions.bioconductor.org/r-code.html>
- Common methods & classes (reuse) — <https://contributions.bioconductor.org/reusebioc.html>
- Package data / Hubs — <https://contributions.bioconductor.org/data.html>
- Documentation & vignettes — <https://contributions.bioconductor.org/docs.html>
- Unit tests — <https://contributions.bioconductor.org/tests.html>
- Version numbering — <https://contributions.bioconductor.org/versionnum.html>
- Review expectations — <https://contributions.bioconductor.org/review-expectation.html>
- Reviewer resources & tools (checklist template + example reviews) — <https://contributions.bioconductor.org/reviewtools.html>
- BiocCheck rule set — <https://bioconductor.org/packages/release/bioc/vignettes/BiocCheck/inst/doc/BiocCheck.html>
