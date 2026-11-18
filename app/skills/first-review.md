---
label: First review
description: A full first review against the Bioconductor package guidelines, with code citations.
model: claude-opus-5-5
when: You haven't reviewed this package yet and want a full first draft to edit (uses the strongest model).
time: ~1 min
---
Draft a full first review.

Work through the package before writing: DESCRIPTION, NAMESPACE, R/ (structure, reuse of Bioconductor classes such as SummarizedExperiment/SingleCellExperiment/GRanges vs reinventing them, vectorisation, sapply/1:n/T/F, error handling, long functions), man/ (examples runnable, \value present, dontrun use), vignettes/ (installation from Bioconductor, evaluates real code, narrative), tests/, inst/, data and file sizes, and the current check findings (get_check_log for bioc-checks).
Always check licensing and provenance (the list at the end): the License field and LICENSE file, code copied, adapted or vendored from elsewhere, AI-assistance disclosure, and where bundled or downloaded data comes from and whether it may be redistributed.
Use search_code to find patterns across files rather than reading everything.
Check data containers explicitly (see the rules): what classes the exported functions accept, what the transform/annotate functions return, and what the vignette's main examples use. If Bioconductor classes aren't accepted, or transformed data doesn't come back in the container it came in, that is the first **Required:** item under `## General package development`, stated concretely (which functions, which class in, which class out), not as a suggestion. Analysis results such as DE tables returned as data.frames are fine; don't ask for those to be stored in the input object.
Read the vignette's introduction: it must state the package's purpose and compare it with existing Bioconductor (and CRAN) packages for the same task, justifying why this package is needed. Don't write your own comparison of packages in the review; react to the submitter's. If the introduction, comparison or justification is missing or thin, ask for it as **Required:**; if it's there, say whether the claimed differences hold up from what you read.
Read the whole thread for submitter comments that no reviewer has answered yet: justifications of check findings, questions, design notes. Address each one in the review, saying whether the justification is accepted under the guidelines and why, with a link to the comment.

Write the review into the draft (write_draft) in the shape Bioconductor reviewers use (from 1,408 past first reviews):
- a short greeting and thanks ("Thank you for submitting your package to Bioconductor!"),
- a summary of 4–6 sentences, in the reviewer's voice, of what the package does and how it is built: the main exported functions and the workflow they form, the data classes going in and out, notable internals (compiled code, external tools, bundled data) and the main dependencies. It shows the submitter what the reviewer understood; keep it factual and from what you read,
- if the submitter left comments that haven't been answered, a short `## Your earlier comments` section answering each (accepted or not, and why, with a link),
- findings grouped under template headings: `## General package development`, `## DESCRIPTION`, `## NAMESPACE`, `## Documentation` / `## Vignette`, `## Man pages`, `## R code`, `## Unit tests`, `## Licensing and provenance` (omit empty ones),
- each finding a checkbox `- [ ]`, one actionable item per box (73% of new-tracker first reviews use checkboxes), citing code as `[R/file.R#L10-L20](permalink)`; mark required vs suggested (`**Required:**` / `Suggested:`), and phrase soft asks as questions,
- a closing request: answer point by point, bump the version to trigger a new build, comment when ready; offer help.
Typical first reviews raise about 13 findings in 3,000–3,400 characters: be specific, not exhaustive.
Only raise a point if you checked it in the source or logs; the checklist below says what reviewers usually look for, not what this package does.
In chat, give a 5-line summary of the most important issues.

## What reviewers raise most often

Distilled from 2,433 past reviews on both trackers (experiments/reviews/out/checklist.md, 2026-11). Percent = share of first reviews raising the item.

**vignette**
- Add an Installation section near the start of the vignette that installs the package from Bioconductor with BiocManager::install('pkg') in a non-evaluated (eval=FALSE) chunk, followed by a library(pkg) load (33%)
- Evaluate vignette code chunks instead of using eval=FALSE, dontrun, verbatim blocks, static images or pseudo-output (24%)
- Make the vignette a narrative: break up large code chunks, explain what each step, function, plot and result shows and why, describe inputs and outputs and the example data, and show how to prepare the user's own data (e.g. as a SummarizedExperiment) (20%)
- Add an Introduction section that works as an abstract: state the package's purpose, objective, input data and distinguishing features compared with similar packages, and explain how it fits into the Bioconductor ecosystem and workflows (16%)
- Format the vignette with BiocStyle, using BiocStyle::html_document as the output format, with BiocStyle in Suggests, and remove duplicated title/author/date header fields (15%)

**coding practice**
- Replace 1:n, 1:length(x), 1:nrow(x), 2:n and seq(1, n) sequences with seq_len() or seq_along() (e.g. seq_along(x)[-1] or tail(x, -1) to skip the first element) so zero-length input does not break loops (25%)
- Replace for/while loops with vectorised code (rowSums/colSums/rowMeans, matrixStats, logical indexing, split(), diff()) or apply-family functions; avoid nested loops and hoist loop-invariant computations out of loops (20%)
- Validate arguments at the start of exported functions (stopifnot, type/length/NA/column-name checks) with informative error messages, and use match.arg() with a choices vector in the signature for arguments with a fixed set of values (19%)
- Use message(), warning() or stop() instead of cat() or print() for user communication; reserve cat/print for show/print methods, and combine multiple calls into one (18%)
- Replace sapply() with vapply() (explicit FUN.VALUE) or lapply() for type-safe results, including in place of unlist(sapply()) or unlist(lapply()); use lengths() instead of sapply(x, length) (16%)

**man pages examples**
- Add a package-level man page (e.g. R/<pkg>-package.R with @docType package / "_PACKAGE", or usethis::use_package_doc()) so ?<pkg> works; give it an overview, links to the main functions with \link, a \seealso, and a pointer to the vignette (15%)
- Document every argument with its expected type, structure, accepted values and defaults, using R terminology such as character(1) and data.frame (12%)
- Add runnable examples to the man page of every exported function, class, constructor and method, so that at least 80% of exported-object man pages have them (12%)
- Remove \dontrun from examples and make them runnable, using small example data, tempfile()/tempdir() for output, and no network access or long run times (9%)
- Document every bundled dataset with its own man page (or one grouped page via @rdname/@aliases) (8%)

**code style**
- Wrap all code lines to 80 characters or fewer in R/, man/, vignettes, NAMESPACE, DESCRIPTION, README, and roxygen comments (long URLs may stay unwrapped) (17%)
- Remove commented-out code, dead code, unreachable code, unused variables and unused functions from R, C/C++, vignette and man files (keep only explanatory comments), and resolve or remove TODO/FIXME comments (15%)
- Indent code with multiples of 4 spaces, using consistent indentation throughout R, C/C++ and Rd files; indent continuation lines of multi-line calls by 4 spaces rather than aligning to the opening parenthesis (15%)
- Use one consistent naming convention (camelCase or snake_case) for functions, arguments, variables and classes; avoid dots in function names to prevent confusion with S3 methods, and start S4 class names with a capital letter (12%)
- Refactor repeated or near-duplicate code blocks and near-identical functions into shared helper functions, or merge them into one parameterised function (e.g. with a method or type argument) (11%)

**DESCRIPTION**
- Declare the minimum R version in Depends as R (>= x.y.z) to match the current Bioconductor release or devel requirement (for example 4.5.0 for release, 4.6.0 for devel) (16%)
- Add a BugReports field pointing to the package's issue tracker (for example the GitHub issues page), as a single valid URL (15%)
- Remove the `LazyData: true` field from DESCRIPTION, or set it to false (14%)
- Expand the Description field into a full paragraph of at least three complete sentences (12%)
- Add biocViews terms from the correct hierarchy, with the 'Software' top-level term where applicable (10%)

**S4 classes reuse**
- Reuse existing Bioconductor classes (SummarizedExperiment, SingleCellExperiment, GRanges/GRangesList, GeneSet/GeneSetCollection, Biostrings, MultiAssayExperiment, etc.) instead of custom classes or plain data.frame/list/matrix structures; if a new class is needed, justify in writing why core classes cannot represent it, or extend an existing class (14%)
- Replace direct slot access (@ or slot()) with accessor functions or methods in package code, examples, vignettes and tests; use @ only inside the accessors themselves (14%)
- Accept standard Bioconductor containers (SummarizedExperiment, SingleCellExperiment, ExpressionSet, MultiAssayExperiment, GRanges, Biostrings classes, etc.) as function inputs in addition to or instead of matrices, data.frames or file paths, extracting assay/coldata internally; select the assay by an argument (default 1) and check the class with is() (10%)
- Return standard Bioconductor objects (SummarizedExperiment, GRanges/GRangesList, DataFrame, etc.) from functions instead of nested lists, data.table, tibble or plain data.frames; keep functions endomorphic where possible and carry over row/column names, colData, seqinfo and metadata (5%)
- Replace S3 classes, class() attribute assignment, and R6/reference classes with formal S4 classes defined via setClass, with show methods and S4 methods in place of print/summary S3 methods (4%)

**NAMESPACE**
- Replace whole-package import() directives with selective importFrom() (or roxygen @importFrom) for packages where only a few functions are used; reserve import() for packages heavily used or whose classes/generics are relied upon (e.g. methods, S4Vectors, SummarizedExperiment) (13%)
- Do not export internal helpers, dot-prefixed functions, S4 method helpers, or functions used only internally or by a Shiny app; keep them unexported (optionally prefix with a dot or use @keywords internal) and remove their man pages, or justify why they are exported (5%)
- Add importFrom() declarations for all functions flagged by R CMD check/BiocCheck as undefined globals or suggested imports, including base-package functions from stats, utils, graphics, grDevices and methods (e.g. importFrom(methods, is, new), stats median/sd, utils head), and declare those packages in Imports (5%)
- Avoid pkg:: calls in package source code for packages not imported in NAMESPACE; import the functions instead and call them unqualified, and recheck imports whenever DESCRIPTION changes so dependency checks are triggered (5%)
- Import every package listed in Depends or Imports in the NAMESPACE (via import/importFrom), and keep DESCRIPTION Imports and NAMESPACE imports in sync: add missing entries, and remove packages that are declared but never used or imported from (4%)

**unit tests**
- Write unit tests for all exported functions, and ideally for internal/helper and non-exported functions, so that the main package functionality and core algorithms are exercised (11%)
- Measure coverage with covr (covr::report() or devtools::test_coverage()), then add tests for files and functions with 0% or low coverage and raise overall coverage substantially, aiming for high coverage (e.g. 80-90%) over time (9%)
- Add a tests/ directory with testthat unit tests (tests/testthat.R plus tests/testthat/test-*.R) that run during R CMD check; replace empty, placeholder, trivial or boilerplate test files with real tests, and use testthat or RUnit but not both (10%)
- Make tests check real behaviour: use expect_* assertions on actual returned values, including numerical correctness against known, hand-computed or reference values with a tolerance, not only output class, structure, or that the code runs without error (2%)
- Test error handling and edge cases: invalid or unexpected inputs, missing arguments, all supported input types (e.g. matrix, SummarizedExperiment, SingleCellExperiment), and input validation, using expect_error/expect_warning/expect_message (2%)

**data ExperimentHub**
- Document every exported dataset in data/ (and any sysdata objects) with a man page or data.R entry giving description, source/reference URL, how it was created (or simulated), object class, rows/columns and column meanings, with the object name matching the file and help topic name (7%)
- Add a script or README under inst/script (not data-raw) documenting how every file in inst/extdata was generated, including source URLs, filtering/processing steps, and licensing, so users can roughly reproduce it (7%)
- Place data in the correct directory: raw files in inst/extdata (accessed via system.file()), processed/exported objects in data/ (documented and loaded with data()), internal objects in R/sysdata.rda, scripts in inst/script, and nothing in data-raw, inst/testdata, the package root or R/ (5%)
- Move large or bulk data to ExperimentHub or AnnotationHub (or a separate experiment data package), with correct metadata.csv fields, S3 upload, distinct titles/descriptions, and rdatapaths; otherwise justify not using a hub (2%)
- Use BiocFileCache (e.g. bfcrpath) to cache all downloaded resources so files are fetched once and persist across sessions, rather than downloading repeatedly, into the working/home/installed directory, or at build time; default to tempdir or a user cache dir if a cache argument is needed (3%)

**dependencies**
- Move packages used only in vignettes, examples, tests, or optional or non-core functions (plotting, Shiny, annotation, Seurat and similar heavy packages) from Imports or Depends to Suggests (3%)
- Replace convenience dependencies with base R or lighter equivalents (4%)
- Remove packages from Imports, Depends and Suggests that the code, vignettes, examples or tests never use (3%)
- Declare every package the code, vignette or tests use in the correct DESCRIPTION field (3%)
- Reuse existing Bioconductor infrastructure instead of reimplementing it (2%)

**build check**
- Run R CMD build and R CMD check (plus BiocCheck) locally on the final package, and fix all errors and warnings (3%)
- Resolve 'no visible binding for global variable' and 'no visible global function definition' notes (3%)
- Check the Bioconductor build report (devel/nightly and single package builder) after each push (2%)
- Remove generated, hidden and non-standard files from the package: inst/doc, doc/, build/, compiled .o/.so files, .Rproj, .DS_Store, .Rhistory, Rplots.pdf, .git, vignette HTML/PDF outputs, build scripts and top-level extras (2%)
- Make the vignette build under R CMD build in the standard build system, without --no-build-vignettes (1%)

**performance**
- Use BiocParallel (e.g. bplapply) for all parallelisation instead of parallel, mclapply, makeCluster, foreach/doParallel/doSNOW, Rmpi or custom backends, or justify why not (5%)
- Vectorise for-loops and nested sapply/lapply iterations (element-wise assignment, matrix index assignment, rnorm/rnbinom draws, column normalisation, string operations, pairwise comparisons) following the Bioconductor efficient-code guidelines (3%)
- Replace apply() over matrix rows or columns with optimised functions: rowSums/colSums/rowMeans/colMeans, or matrixStats equivalents (rowMins, rowMaxs, colMedians, rowVars, colSds, colWeightedMeans) (2%)
- Expose a `bpparam` argument on every parallelised function, defaulting to `BiocParallel::bpparam()` or `SerialParam()` (not NULL) (1%)
- Pre-allocate result vectors, lists and matrices instead of growing them by copy-and-append (c(), rbind/cbind in loops, repeated merge) (2%)

**fit overlap**
- Explain in the vignette introduction and DESCRIPTION how the package differs from existing Bioconductor and CRAN packages of similar scope, and name those packages concretely (4%)
- Split the package if it mixes distinct audiences or concerns, such as analysis, plotting, Shiny apps, infrastructure, data, utilities or reporting (2%)
- Use standard Bioconductor data structures (SummarizedExperiment, SingleCellExperiment, SpatialExperiment, MultiAssayExperiment, GRanges/GRangesList, Biostrings classes, TreeSummarizedExperiment, and so on) for inputs and outputs (1%)
- Do not reimplement algorithms or statistical methods that already exist in established packages (2%)
- Reuse existing Bioconductor file import and export functions instead of writing custom parsers or writers (1%)

**BiocCheck**
- Run BiocCheck::BiocCheck() (and BiocCheckGitClone() on the repository) after every update, then fix all reported errors and warnings and as many notes as possible (5%)
- Go through the build report (R CMD check and BiocCheck output) line by line and resolve every error, warning and note, including typos and other minor items (2%)
- Resolve 'no visible binding' and 'no visible global function definition' notes by importing the needed functions (importFrom, including from methods), using .data, qualifying calls with pkg::, or declaring variables with utils::globalVariables() (1%)
- Fix DESCRIPTION issues: set Depends R to the required version, remove LazyData or set it to false, add a valid ORCID for the maintainer and a fnd role if applicable, and make sure URL and BugReports fields are present (1%)
- Clarify how objects flagged as undefined or uninitialized are created, for example via data(), with() or within(), so the checker can see their definition (1%)

## Licensing and provenance (always check)

From the guidelines, not the corpus: DESCRIPTION `License` (https://contributions.bioconductor.org/description.html#description-license) and the AI policy and third-party code chapter (https://contributions.bioconductor.org/ai-policy-third-party.html). Mark as **Required** when a rule is broken, and ask when information is missing.
- `License` is a standard license with its version, or `file LICENSE` with the full terms; restrictive licenses (CC BY-NC, -NC-SA, -NC-ND, ACM, academic or non-commercial only) are not acceptable; `+ file LICENSE` must match the LICENSE file
- Code copied, adapted or vendored from elsewhere (search for "adapted from", "copied from", "Copyright", "Licensed under", other projects in `src/`, JS/CSS in `inst/`) is cited in the code, its license allows redistribution under the package's license, and its copyright holders are credited (`cph` in `Authors@R`)
- Non-trivial copied or AI-generated code is disclosed in the issue with its provenance (`Assisted-by:` / `Code copied from:`); raise only concrete signs, not style hunches
- Every bundled dataset and file in `inst/extdata`, and data that examples or vignettes download, has a stated source and license or terms that allow redistribution; human-subject data says it is de-identified and may be shared
