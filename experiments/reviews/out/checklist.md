# Review checklist distilled from past reviews

Source: 2,433 long reviewer comments on 1,657 submissions (120 new tracker, 2,313 legacy); 1,408 classified as first full reviews (101 new, 1,307 legacy). Method and caveats: `experiments/reviews/LEDGER.md`.

Columns: **reviews** = comments raising the item (any kind); **first** = share of first full reviews raising it, overall / new tracker / legacy. Items are ordered by reviews. Typical wording is quoted verbatim from first reviews (two different reviewers where possible). New-tracker shares rest on few reviews (101), so treat differences under ~10 points as noise.

| Category | reviews | first | first (new) | first (legacy) |
|---|---|---|---|---|
| [vignette](#vignette) | 1,535 | 84% | 87% | 84% |
| [coding_practice](#coding_practice) | 1,390 | 76% | 72% | 76% |
| [other](#other) | 1,134 | 63% | 79% | 62% |
| [man_pages_examples](#man_pages_examples) | 1,131 | 60% | 54% | 61% |
| [code_style](#code_style) | 1,121 | 66% | 53% | 67% |
| [DESCRIPTION](#description) | 1,046 | 64% | 63% | 64% |
| [S4_classes_reuse](#s4_classes_reuse) | 963 | 50% | 55% | 50% |
| [NAMESPACE](#namespace) | 713 | 42% | 38% | 42% |
| [unit_tests](#unit_tests) | 696 | 41% | 44% | 41% |
| [data_ExperimentHub](#data_experimenthub) | 585 | 31% | 33% | 30% |
| [dependencies](#dependencies) | 490 | 26% | 36% | 25% |
| [process](#process) | 472 | 16% | 20% | 15% |
| [build_check](#build_check) | 368 | 15% | 16% | 15% |
| [performance](#performance) | 306 | 17% | 16% | 17% |
| [fit_overlap](#fit_overlap) | 301 | 17% | 22% | 16% |
| [BiocCheck](#bioccheck) | 260 | 15% | 24% | 14% |

## vignette

_vignettes: content, installation chunk, eval=FALSE, sessionInfo, style_

| # | Item | reviews | first | new | legacy |
|---|---|---|---|---|---|
| 1 | Add an Installation section near the start of the vignette that installs the package from Bioconductor with BiocManager::install('pkg') in a non-evaluated (eval=FALSE) chunk, followed by a library(pkg) load. Use BiocManager rather than BiocInstaller/biocLite, devtools, install.packages or lab-website instructions. | 510 | 33% | 41% | 32% |
| 2 | Evaluate vignette code chunks instead of using eval=FALSE, dontrun, verbatim blocks, static images or pseudo-output. Use small or packaged example data so all user-facing code runs during the build, and fix any chunks that error or warn. Keep eval=FALSE only for installation or truly impractical chunks, and justify those. | 435 | 24% | 27% | 24% |
| 3 | Make the vignette a narrative: break up large code chunks, explain what each step, function, plot and result shows and why, describe inputs and outputs and the example data, and show how to prepare the user's own data (e.g. as a SummarizedExperiment). | 351 | 20% | 34% | 19% |
| 4 | Add an Introduction section that works as an abstract: state the package's purpose, objective, input data and distinguishing features compared with similar packages, and explain how it fits into the Bioconductor ecosystem and workflows. | 258 | 16% | 38% | 15% |
| 5 | Format the vignette with BiocStyle, using BiocStyle::html_document as the output format, with BiocStyle in Suggests, and remove duplicated title/author/date header fields. | 220 | 15% | 22% | 14% |
| 6 | Add a table of contents to the vignette (e.g. via BiocStyle::html_document with toc: true), and use single-# top-level and ## subsection headers so numbering is correct. | 174 | 11% | 12% | 10% |
| 7 | Write all files produced by vignette code (and examples) to tempdir() or tempfile(), not getwd() or the package directory. Load example data via system.file() or packaged/ExperimentHub data rather than downloading it or using hard-coded paths. | 171 | 9% | 9% | 9% |
| 8 | Demonstrate a complete worked example of the package's main functionality, using real or realistic data, interpreting results, and showing integration with standard Bioconductor classes and packages, rather than only minimal calls or man page repetition. | 170 | 10% | 21% | 9% |
| 9 | Format package, function and argument names as code (backticks) and fix Markdown rendering problems (headings after code chunks, bullet lists, links, non-ASCII characters). Use BiocStyle helpers such as Biocpkg() and CRANpkg() for linking packages. | 170 | 10% | 13% | 9% |
| 10 | End the vignette with a Session info section containing a chunk that calls sessionInfo() and prints its output. | 168 | 11% | 6% | 11% |
| 11 | Load the package and any other libraries once at the top of the vignette (setup chunk, message=FALSE where needed), and remove library() calls for unused packages, Imports/Depends packages, and redundant :: prefixes. | 155 | 8% | 7% | 8% |
| 12 | Spell-check and proofread the vignette, fixing typos, grammar and wording, spacing after punctuation, correct capitalisation of Bioconductor and package names, and defining acronyms at first use. | 150 | 8% | 8% | 8% |
| 13 | Name the main vignette file after the package (e.g. pkg.Rmd) so vignette('pkg') works. Give it a descriptive title, make vignetteIndexEntry match that title, and include the VignetteEngine and encoding fields on separate lines. | 147 | 9% | 7% | 9% |
| 14 | Keep only vignette sources (.Rmd/.Rnw), bibliography and needed images in the vignettes directory. Remove generated or build products (html, pdf, tex, log, .R from Stangle, cache and figure folders, index.Rmd, unused images) from the repository and vignettes/inst/doc. | 142 | 9% | 2% | 9% |
| 15 | Remove GitHub, devtools, local-tarball, R CMD INSTALL and platform-specific installation instructions, git clone steps, and explicit dependency-installation steps or dependency lists from the vignette. Mention a development-version install only via BiocManager, with a caution. | 141 | 9% | 7% | 9% |
| 16 | Follow good coding practice in vignette code: use <- for assignment, avoid @ slot access in favour of accessors, avoid explicit print() or show() and rm(list=ls()), set a seed where results are random, and use head() to limit large output. | 132 | 8% | 4% | 8% |
| 17 | Give every code chunk a distinct, descriptive label, use proper {r} chunk headers, and remove redundant chunk options (eval=TRUE, echo=FALSE on setup, globally suppressed warnings/messages, cache=TRUE). | 113 | 6% | 6% | 6% |
| 18 | Fix broken or undefined references, citations, cross-references, hyperlinks and image links so they render correctly in the built vignette, and give the references their own section. | 103 | 6% | 8% | 6% |
| 19 | Keep vignette text and code lines within 80 columns, wrapping long code lines and comments so they do not run off the page in the rendered output. | 98 | 6% | 0% | 7% |
| 20 | Remove commented-out code, placeholder or unfinished text, and incomplete sentences or sections from the vignette. Either complete or delete empty sections and empty references. | 95 | 6% | 3% | 6% |
| 21 | Add title, author names with affiliations, and a fixed last-modified date to the vignette header, instead of Sys.Date(). | 32 | 2% | 1% | 2% |
| – | _unmatched points_ | 283 | | | |

Typical wording:

- 1. “Do not use `devtools::install_github` in your vignette to install the package.”
- 1. “Please include Bioconductor installation instructions using BiocManager.”
- 2. “Is there a reason not to evaluate this code block? We would like to see user facing code evaluated by the builder”
- 2. “It looks like the show method print out from line 122 in the vignette is missing something:”
- 3. “An appropriate vignette provides text, code, and results (e.g., summary output and figures) that walk the user through a typical use case.”
- 3. “please provide more detail in the vignette and man page for package/main function on what/how the normalization is performed.”
- 4. “Would be nice if the Introduction of the _Basic usage_ vignette could provide a little bit more background information”
- 4. “Please expand the introduction in the main vignette to describe the package in more detail.”
- 5. “Vignette uses `BiocStyle` package for formatting. Strongly encourage rendering as html (over pdf, etc)”
- 5. “You don't have to load `BiocStyle` to apply its style.”
- 6. “Especially if you have lengthy vignettes, we highly suggest the use of table of contents.”
- 6. “Please add a table of contents to the vignette.”
- 7. “Load data appropriately using `system.file` in your example.”
- 7. “The vignette and examples should not be acquiring data from remote sites, in my opinion, unless this can be accomplished rapidly and in a fail-safe manner.”
- 8. “In particular connect your contribution to other opportunities within the Bioconductor ecosystem, illustrating how the inputs and outputs to your package are relevant to other steps”
- 8. “I know the instructions are currently spread into different vignettes but we should have the core functions in the introduction.”
- 9. “I would have a title above each panel, and decide if all should be bold or not (E is the only one that isn't bold).”
- 9. “Strongly recommend proofreading the rendered vignette to check it appears as you intend”
- 10. “The final section of the vignette should be 'Session Information' and should include `sessionInfo()`.”
- 10. “Add `sessionInfo()` in the end of vignette”
- 11. “The vignette ought to have a section near the beginning explaining installation.”
- 11. “You do not need to load in all of the libraries for your package in your vignette.”
- 12. “Line 22, you mention VisualExperiment and not SpatialExperiment.”
- 12. “Rephrasing "downstream analyses that [help can] interpret the MCIA decomposition."”
- 13. “Please rename `vignettes/drugannot.Rmd` to `drugannotR.Rmd`”
- 13. “I recommend the name of the package uncoverappLib.Rmd.”
- 14. “Remove `proBatch_vignette_brief.R` and only keep the `.Rmd` files and `.png` files.”
- 14. “No need to have the `html` file, as the build system will run the vignette and generate the html file.”
- 15. “Same comment about instructions for `PhIPData`”
- 15. “Packages_installation.Rmd is irrelevant and should be removed.”
- 16. “No need to explicitly use `print()` in the vignette”
- 16. “Use `<-` for assignment instead of `=` to adhere to R conventions.”
- 17. “you include a section of code that is not echoed and the results are hidden. This isn't best practice”
- 17. “Consider adding `fig.width/height` flags to corresponding code chunks to control this.”
- 18. “Use the `bibliography:` field in the RMarkdown YAML front matter and create an `../inst/REFERENCES.bib` file”
- 18. “There seems to be a missing reference for 'Biostrings'. The link in the second paragraph of the 'Introduction' links back to your vignette.”
- 19. “Pay attention to long code lines, since these wrap poorly in the vignette”
- 19. “Consider restricting the text to 80 column width. It makes it easier to review and maintain.”
- 20. “The Citation subsection is empty. Since you have References as the last section of the vignette I would consider removing the Citation subsection.”
- 20. “There's a "References" section but not references; remove it?”
- 21. “It should display the name of the author(s).”
- 21. “Remove `Sys.time` calls from vignette. These will be provided by the BBS.”

## coding_practice

_vapply/sapply, seq_len/1:n, loops and vector growth, T/F, message vs cat/print, set.seed, file paths, browser(), suppressWarnings_

| # | Item | reviews | first | new | legacy |
|---|---|---|---|---|---|
| 1 | Replace 1:n, 1:length(x), 1:nrow(x), 2:n and seq(1, n) sequences with seq_len() or seq_along() (e.g. seq_along(x)[-1] or tail(x, -1) to skip the first element) so zero-length input does not break loops. | 405 | 25% | 6% | 26% |
| 2 | Replace for/while loops with vectorised code (rowSums/colSums/rowMeans, matrixStats, logical indexing, split(), diff()) or apply-family functions; avoid nested loops and hoist loop-invariant computations out of loops. | 333 | 20% | 24% | 20% |
| 3 | Validate arguments at the start of exported functions (stopifnot, type/length/NA/column-name checks) with informative error messages, and use match.arg() with a choices vector in the signature for arguments with a fixed set of values. | 326 | 19% | 21% | 19% |
| 4 | Use message(), warning() or stop() instead of cat() or print() for user communication; reserve cat/print for show/print methods, and combine multiple calls into one. | 290 | 18% | 12% | 19% |
| 5 | Replace sapply() with vapply() (explicit FUN.VALUE) or lapply() for type-safe results, including in place of unlist(sapply()) or unlist(lapply()); use lengths() instead of sapply(x, length). | 252 | 16% | 7% | 16% |
| 6 | Do not wrap arguments in paste()/paste0() inside message(), warning(), stop() or cat(); pass multiple arguments directly, and make messages informative, concise and without 'Error:' prefixes or exclamation marks. | 226 | 14% | 11% | 14% |
| 7 | Reduce code repetition by factoring duplicated logic and repeated checks into internal helper functions, and replace long if/else chains with switch() or lookup tables. | 184 | 10% | 8% | 10% |
| 8 | Do not write files to the user's working directory or file system by default; write to tempdir()/tempfile() in examples, vignettes and tests, return objects instead, and make saving optional with an explicit path and overwrite argument. | 146 | 8% | 9% | 8% |
| 9 | Do not grow vectors, lists, matrices or data frames by copy-and-append (c(), append, rbind/cbind in loops); pre-allocate and fill, or use lapply/vapply and combine once with do.call(rbind, ...). | 137 | 8% | 4% | 8% |
| 10 | Do not change global state in package code: remove setwd(), options() changes, par changes and assignments into the global environment, or restore them with on.exit(); avoid <<-, assign() and get(). | 109 | 6% | 8% | 6% |
| 11 | Write TRUE/FALSE in full instead of T/F, and do not compare logicals to TRUE/FALSE or use isTRUE/ifelse needlessly; test logical flags directly, use && and || in if conditions, and use if/else instead of ifelse() for scalars. | 106 | 6% | 3% | 6% |
| 12 | Remove leftover debugging and unnecessary calls: browser(), rm(), gc(), flush.console(), Sys.sleep(), no-op paste/c()/return() calls and unused variables. | 105 | 6% | 5% | 6% |
| 13 | Build file paths with file.path() or system.file() instead of paste/paste0 or hard-coded separators; do not hard-code local or /tmp paths. | 86 | 5% | 2% | 5% |
| 14 | Avoid suppressWarnings()/suppressMessages(); fix the underlying cause or handle the edge case, and if unavoidable wrap only the specific call. | 85 | 5% | 5% | 5% |
| 15 | Refer to columns and list elements by name rather than numeric index, and use [[ ]] instead of $ for list access. | 74 | 4% | 4% | 4% |
| 16 | Use is() or inherits() (or is.numeric/is.character etc.) instead of comparing class(x) with ==, and use methods::is for S4 classes. | 73 | 4% | 1% | 5% |
| 17 | Use logical vectors directly for subsetting instead of which(), and use simplified idioms such as anyNA(), nrow()/ncol(), if (length(x)) and sum(!is.na(x)). | 72 | 4% | 0% | 5% |
| 18 | Add a verbose argument (default FALSE) to control progress and diagnostic messages, and drop unnecessary startup or status output. | 64 | 4% | 6% | 4% |
| 19 | Remove library(), require() and source() calls from package code; rely on imports declared in DESCRIPTION/NAMESPACE, use requireNamespace() for optional packages, and do not install packages dynamically. | 63 | 4% | 6% | 4% |
| 20 | Remove set.seed() calls from package functions; leave seeding to the user or add a seed argument. | 55 | 3% | 9% | 3% |
| 21 | Avoid eval(parse(text=...)), try() and overbroad tryCatch; check error conditions explicitly, and wrap web/download calls in tryCatch with limited retries so failures degrade gracefully. | 51 | 3% | 1% | 3% |
| 22 | Use drop=FALSE when subsetting matrices, arrays and data frames so dimensions are preserved. | 46 | 3% | 4% | 3% |
| 23 | Avoid redundant :: qualifiers for packages already imported and for the package's own functions. | 44 | 3% | 4% | 3% |
| 24 | Use the native pipe |> instead of magrittr %>% in package code, and use <- rather than = for assignment. | 39 | 2% | 1% | 3% |
| 25 | Use system2() instead of system() (and check its status), or base R/R-native functions (tar/untar, etc.) instead of shell calls. | 29 | 2% | 2% | 2% |
| – | _unmatched points_ | 360 | | | |

Typical wording:

- 1. “Please use `seq_along()`/`seq_len()` instead of `1:...`”
- 1. “Prefer `seq_len()`/`seq_along()` over `1:...` (see notes in multiple files).”
- 2. “It seems that the nested for-loop is not necessary (j is not used in the loop and it does not seem like each iteration is adding anything new).”
- 2. “Consider changing for loops to vapply (recommended) or lapply.”
- 3. “Function arguments should have some validation and checking for correct user input.”
- 3. “it would be sensible to implement some minimal argument checks in order to prevent (potentially heavy) computations from being carrier out”
- 4. “Condense `message` functions into one (`R/enrichment.R`).”
- 4. “Remove `print(w)` and replace with `message` instead (l:85 internal_spline_function.R"). Make this correction in every place `print` was used.”
- 5. “Avoid using `sapply`. Use either `lapply` or `vapply` if the return is predictable.”
- 5. “Avoid sapply(); use vapply() found in files: CorrectGapsAndNs.R (line 15, column 12) ...”
- 6. “If there is an error ... use `stop()` making sure that the error tells the user what you have been checking”
- 6. “in unitTest, if they are "ERROR" consider using `error()` instead of `cat(paste0(`”
- 7. “Functional programming: code repetition. repetition in `callQTL`, `linearModel`, `poissonModel`, `visualizeQTL`, and `zinbModel`”
- 7. “`setGeneric("sbivar")` is called twice with different signatures; the second silently replaces the first. Remove one.”
- 8. “use `fl <- tempfile(); dir.create(fl)` rather than `getwd()`, `~/`, or other directories in the user's file system.”
- 8. “Do not create a log by default in the users working directory. Consider setting the path to the `tempfile` or not creating one unless the users provides a path for it.”
- 9. “Avoid using copy-and-append methods with for loops, use the allocate and fill method (`buildAvgLoading`).”
- 9. “Instead, read the data as a data.frame and operate on the columns as vectors.”
- 10. “Do not set `options` without resetting them to the original setting.”
- 10. “Avoid `assign` calls in the `.onLoad` function and simply set package constants within an R file”
- 11. “There are some instances ... where you use `"FALSE"` or `"TRUE"` as character rather than logical values.”
- 11. “if (is.numeric(size) & all(size >= 1)) ctr$size = floor(size[1:2]) else message("size")”
- 12. “In function `df2mat` you already removed the colnames and rownames, but you call remove them again at line 158-159.”
- 12. “You seem to be using the function `rm` to remove some object. This is not needed, if you are "saving" memory.”
- 13. “clinical <- read.csv("../inst/extdata/1-s2.0-S0092867421014860-mmc1.csv")”
- 13. “Please use `file.path()` instead of `paste0()` to construct file paths”
- 14. “Generally it seems like warnings should not be supressed if the function is being used appropriately.”
- 14. “You have wrapped several calls to `ggplot` in `suppressWarnings()`. This is not recommended, as it can hide important warnings.”
- 15. “Increase robustness by using named indices rather than numeric ones.”
- 15. “Consider either documenting that these names are required or allowing users to specify them through function arguments”
- 16. “Avoid the use of `class(x) == "class"` language. If you are testing for S3 class membership, use `inherits()` or use `is()` for S4 classes.”
- 16. “use `inherits()` (S3) or `is()` (S4) rather than `class()`.”
- 17. “Logical to Numeric index switching not necessary most of”
- 17. “using `%in%`, an edge case maybe that the file has 2 or more columns named as `id`”
- 18. “asking users to run it separately when running `cellassign` by possibly using a wrapper function so that the user can set `verbose = TRUE` / `FALSE`”
- 18. “consider adding a `verbose = TRUE/FALSE` argument to allow users to control whether progress messages are printed to the console.”
- 19. “Please remove `suppressMessage(require(...))`. Since these packages have already been included in `DESCRIPTION, Imports`”
- 19. “This is not needed since `ggplot2` is listed in `Imports` and therefore guaranteed to be available when `MeLSI` is installed.”
- 20. “Do NOT manipulate the random number generator `set.seed()` inside function.”
- 20. “`trio$split()` taking a `seed` argument runs counter to usual advice to `set.seed()` before calling a function.”
- 21. “preferred style is to use `tryCatch()` rather than `try()` and `if (inherits...)`”
- 21. “Data accessed from the web should be cached. We recommned BiocFileCache. You should also implement some graceful tryCatch”
- 22. “Please consider to add `drop=FALSE` to avoid the reduction of dimension for matrices and arrays.”
- 22. “`map[, !names(map) %in% c("exon_id", "transcript_id"), drop = FALSE]`.”
- 23. “Also for the workflow.R, again you should remove the "::" as the functions will be available after the library(package) invocation.”
- 23. “It is not necessary to use the `base::` qualifier for default functions.”
- 24. “Consider using the native pipe `\|>` over the `magrittr` pipe.”
- 24. “Please use `<-` instead of `=` for assignment in your code.”
- 25. “Bioconductor recommends `system2` over `system` for the call in the benchmarking script.”
- 25. “Please use `system2` instead of `system`”

## other

_anything else (README, NEWS, licensing of code, inst/ scripts, Shiny...)_

| # | Item | reviews | first | new | legacy |
|---|---|---|---|---|---|
| 1 | Add Bioconductor installation instructions to the README using BiocManager::install() (not install_github, install.packages, source/biocLite or a pinned version), and link to the Bioconductor landing page/vignette. Before acceptance, show these as an eval=FALSE section. | 216 | 14% | 26% | 13% |
| 2 | Add a NEWS file (top-level or inst/NEWS) that records user-facing changes per version, so it is included in release announcements. Populate it with real entries, or remove it if it will not be maintained. Do not leave it empty or as a template. | 186 | 12% | 6% | 12% |
| 3 | Organise R code into logically coherent files, merging or removing redundant, unused, commented-out or half-implemented functions. Consolidate near-duplicate functions into parameterised ones, and use descriptive, non-conflicting function, argument, dataset and package names. | 143 | 8% | 13% | 7% |
| 4 | Remove files that are not part of the package from the repository, or explain why they are needed: .Rproj, .Rhistory, .RData, .DS_Store, Thumbs.db, backup files (*~, .bak), build/, docs/, rsconnect/, PDFs/PNGs at top level, stray scripts, and 'read-and-delete-me'. Add the IDE and generated-file patterns to a single top-level .gitignore and .Rbuildignore. | 141 | 8% | 13% | 8% |
| 5 | Format the NEWS file so utils::news() parses it: use 'Changes in version x.y.z' headings (without the package name), bullet list items (+ or *), no empty sections, no separator lines or code fences, and a single NEWS file in one supported format. | 137 | 8% | 5% | 9% |
| 6 | Add a top-level README (README.md) that describes what the package does, its expected input, how to install it, how to cite it, and how to report issues or contribute. Make sure example code runs and links and images work. Keep only one README format (or keep .md and .Rmd in sync). | 102 | 6% | 10% | 6% |
| 7 | Add inst/scripts documenting how each inst/extdata file and each data/ object was generated, including sources, URLs, processing and licensing. Move data-raw scripts into inst/scripts, and move any publication or dataset generation code there too. | 98 | 6% | 4% | 6% |
| 8 | Add an inst/CITATION file for the associated publication or preprint, and make sure it parses with readCitationFile (declare encoding for non-ASCII characters, no placeholders or blank file). | 84 | 5% | 18% | 4% |
| 9 | Explain the purpose of non-standard directories and files (inst subdirectories, sysdata.rda, datalist, misc/, templates, top-level scripts) or remove them. Use standard names such as inst/extdata and inst/scripts. | 72 | 5% | 3% | 5% |
| 10 | Keep only the files each directory is meant to hold. vignettes/ holds only vignette sources and needed assets (no generated .html/.R/.pdf/.tex, no helper scripts or docs). man/ holds only .Rd files (move figures to inst/figures). R/ holds only R code. Remove duplicated copies of vignettes in inst/doc. | 70 | 5% | 5% | 5% |
| 11 | Resolve licensing problems. Remove LICENSE or LICENSE.md files when a standard license is declared in DESCRIPTION, or make them match the DESCRIPTION. Fill in template placeholders. Keep only one license file. | 69 | 4% | 1% | 5% |
| 12 | Keep the NEWS version headings consistent with the DESCRIPTION version and the package's real version history (e.g. 0.99.0 at submission), and update NEWS with each version bump. | 63 | 4% | 7% | 4% |
| 13 | Run a spell checker (e.g. the spelling package) over the documentation, vignette, README, code comments and messages, and fix the typos. | 61 | 3% | 3% | 4% |
| 14 | Keep Shiny app code inside the package, in R/ functions, with the app launched via a documented function. Don't hardcode paths, use Docker, or source files at runtime, and make the app handle errors and invalid input gracefully. Consider a separate package for large apps. | 59 | 3% | 2% | 3% |
| 15 | Clarify where objects used in examples and functions are initialised (data(), with(), etc.) and give arguments sensible defaults and early validation. | 59 | 3% | 7% | 3% |
| 16 | Remove or minimise startup and user messages: no .onAttach/.onLoad banners, no exclamation marks, jokes or emoji. Add a verbose argument to control messages, and make messages accurate. | 55 | 3% | 3% | 3% |
| 17 | Comply with third-party code and data license requirements. Retain the original license and acknowledge authorship for any bundled code, confirm that redistribution of code and data is permitted, and prefer importing from the upstream package or contributing fixes upstream over copying code. | 51 | 3% | 9% | 2% |
| 18 | Do not write files (plots, PDFs, tables, caches, dot files) to the user's directory or the installed package directory without explicit consent. Provide output-location arguments, return objects instead, and let users save plots themselves. | 49 | 2% | 0% | 3% |
| 19 | Separate computation from plotting and file I/O. Return results or ggplot objects that plotting functions can consume, and remove file-name or PDF arguments from analysis functions. | 42 | 2% | 4% | 2% |
| 20 | Keep pkgdown, CI and other development configuration (_pkgdown.yml, docs/, codecov.yml, .github, .gitlab-ci.yml, dev/, cran-comments.md) out of the branch Bioconductor builds. Move it to a separate branch or add it to .Rbuildignore. | 40 | 2% | 4% | 2% |
| 21 | Follow the Bioconductor guidelines for web resources: cache downloads, fail gracefully when the network is unavailable, and avoid hard-coded or unstable URLs and untrusted hosting such as Dropbox. | 34 | 2% | 3% | 2% |
| 22 | Declare and register native code properly and handle system requirements. Register routines with R_registerRoutines and R_useDynamicSymbols(FALSE), and document installation steps for non-trivial system dependencies in an INSTALL file or README section. | 33 | 1% | 2% | 1% |
| 23 | Follow the Bioconductor package guidelines on package size, check time, tarball and repository size, and R CMD build --resave-data, and address any previous review items that remain open. | 25 | 1% | 2% | 1% |
| – | _unmatched points_ | 189 | | | |

Typical wording:

- 1. “in the README, please add installation instruction using `BiocManager::install()`”
- 1. “Add installation for release via BiocManager to README and vignette.”
- 2. “in the NEWS, remember to keep track of changes, in non-technical language”
- 2. “Please add a `NEWS` file that keeps track on the changes you introduce to the package.”
- 3. “Perhaps you can combine these functions into one and add an arugment for either `quality` or `stability`?”
- 3. “Why is this needed and not just directed to the HDF5Array function when necessary?”
- 4. “What are the purpose of these directories? They probably should not be git tracked?”
- 4. “What is the purpose of the 'docs/' directory. This is not a directory that we normally allow in Bioconductor package and won't be included.”
- 5. “be careful to keep this accurate and in a format that can be parsed by `utils::news()`.”
- 5. “Check the format of the NEWS file, when I installed the package and tried `utils::news(package = "microSTASIS")` it didn't render properly”
- 6. “Are both of these files necessary? Is there a concern for one getting out of date of the other?”
- 6. “Please clarify how **anndataR** relates to existing tools, including the CRAN **anndata** package and Bioconductor **zellkonverter** package.”
- 7. “move data-raw and Meta to proper position (eg inst/extdata).”
- 7. “Ideally, and for the sake of reproducibility, the code used to generate them should be made available.”
- 8. “Consider adding a [`inst/CITATION` file]”
- 8. “consider adding a CITATION file linking this”
- 9. “Why do these files have to get installed along with the package? I don't understand how they are adding value.”
- 9. “There is a sysdata.rda file in the R/ directory. Is this file needed?”
- 10. “Remove the Stangled file `GmicR_vignette.R`. It shouldn't be needed in the repo.”
- 10. “*unacceptable* files present ./vignettes/seqpac_-_A_guide_to_sRNA_analysis_using_sequence-based_counts.pdf”
- 11. “You distribute based on GPL but reference http://www.apache.org/licenses/LICENSE-2.0 in your R code. Are these two license consistent with each other?”
- 11. “The LICENSE contains placeholders such as "name of author", "year" etc. Please fill these in.”
- 12. “Please make sure there is at least one entry in the `NEWS` file and that versions match package versions”
- 12. “Make sure to keep `NEWS.md` up-to-date: the last entry is for 0.99.1, while the package is at 0.99.2.”
- 13. “Please correct spelling errors `datra.frame`, `at list 3 columns`, etc.”
- 13. “There are some spelling issues, though minor, it would be good to clear these up e.g.: “gorvened”, “whcih””
- 14. “I ran the shiny app and kept getting an error: `object 'idx' not found`. After selecing `Hsapiens.UCSC.hg19` in the setup tab.”
- 14. “I'm also very surprised to see that `startStandalone()` needs to clone a git repo.”
- 15. “Consider clarifying how 2 objects are initialized.”
- 15. “What values can host have ... only the one default? If there can be more than one value how do I discover what these are?”
- 16. “Please choose a more modest welcome banner in `.onAttach()`”
- 16. “and 'Don't worry' / 'ADVICE' directives (in `PerformParamsOptimization`).”
- 17. “Have you discussed this with them? Having HTSlib support openMP would be a much more satisfying solution than your proposal.”
- 17. “I do not think use of GSEA.jar is appropriate, and this should be removed from your package.”
- 18. “you display plots when performing the analysis. are there options to save these.”
- 18. “Package specific cache locations can be set using”
- 19. “Would it be better to return the `ggplot` object instead of just a printed out image that the user cannot manipulate?”
- 19. “I would suggest considering separating the computation from the visualization, and provide a parameter that allows the user to choose whether to export the generated plots”
- 20. “CLARIFICATION: What is the purpose of the 'codecov.yml' file?”
- 20. “*unacceptable* files present (see .gitignore for a listing). please move it to a different branch. * docs/*”
- 21. “We do not allow data to be hosted on random sites like dropbox.”
- 21. “Since you make queries to web resources be sure you are following our guildesline here.”
- 22. “I'm highly skeptical of the need for the volume of C++ code in this package”
- 22. “Please check that your C code checks for user interruptions”
- 23. “I had a problem with running `R CMD build` locally where the vignette did not finish building”
- 23. “complete TODO tasks before submitting a revised version.”

## man_pages_examples

_Rd/roxygen documentation, runnable examples, \dontrun, @return_

| # | Item | reviews | first | new | legacy |
|---|---|---|---|---|---|
| 1 | Add a package-level man page (e.g. R/<pkg>-package.R with @docType package / "_PACKAGE", or usethis::use_package_doc()) so ?<pkg> works; give it an overview, links to the main functions with \link, a \seealso, and a pointer to the vignette. | 238 | 15% | 21% | 14% |
| 2 | Document every argument with its expected type, structure, accepted values and defaults, using R terminology such as character(1) and data.frame. Make @param entries match the actual function signature and \usage, and remove entries for arguments that do not exist. | 230 | 12% | 10% | 12% |
| 3 | Add runnable examples to the man page of every exported function, class, constructor and method, so that at least 80% of exported-object man pages have them. | 198 | 12% | 13% | 12% |
| 4 | Remove \dontrun from examples and make them runnable, using small example data, tempfile()/tempdir() for output, and no network access or long run times. Justify any remaining \dontrun in a comment. | 157 | 9% | 6% | 9% |
| 5 | Document every bundled dataset with its own man page (or one grouped page via @rdname/@aliases). Include a proper title, \format describing the class, dimensions and the meaning of each column, \source and provenance, how the data were generated, and a data() example. | 153 | 8% | 5% | 8% |
| 6 | Fix typos, spelling, wrong function or package names, stale references, and broken Rd markup or cross-references. Use \code{} rather than backticks, spell out acronyms, and run a spell check on the man pages. | 148 | 7% | 4% | 7% |
| 7 | Expand sparse man pages: write a descriptive \description and \details explaining what each function or class does, how, and when to use it, rather than repeating the title or the function name. | 119 | 7% | 2% | 7% |
| 8 | Make sure every example runs without error or warning and demonstrates the function it documents. Fix examples that call undefined objects, missing files, deprecated arguments or unexported functions (:::). Do not leave placeholder examples that only print a message. | 111 | 5% | 5% | 6% |
| 9 | Add a non-empty \value section (@return) to every man page. Describe the returned object's class, structure, dimensions, names and columns, and make it match what the function actually returns. | 110 | 5% | 5% | 5% |
| 10 | Mark documented but non-exported or internal functions with @keywords internal (or stop documenting them), and make sure every exported object has a man page. | 100 | 6% | 6% | 6% |
| 11 | Where an example truly cannot run during checks (slow or external resources), use \donttest instead of \dontrun, and use if (interactive()) for interactive-only code. Do not comment out example code, use if (FALSE), or use \dontshow to inflate coverage; make sure code inside \donttest is valid and executed somewhere (vignette or tests). | 99 | 5% | 5% | 5% |
| 12 | Document S4/R5/S3 classes fully: describe the structure and slots, the constructor and accessors, and add \seealso links. Combine related methods, generics and constructors onto shared pages with @rdname or @describeIn, and remove man pages for generics or functions that do not exist. | 77 | 4% | 2% | 4% |
| 13 | Document the origin and structure of example data used in man pages. Reference any generating scripts in inst/scripts, and describe the expected input format (columns, classes, SummarizedExperiment support) and the algorithm or publication behind each main function. | 66 | 4% | 3% | 4% |
| 14 | Clean up example code: remove library() calls for the package itself or for packages already in Depends/Imports, avoid pkg:: qualifiers where unnecessary, load needed Suggests packages, and use system.file() or file.path() for paths. | 58 | 2% | 2% | 2% |
| 15 | Move man/figures and other non-Rd files out of the man directory into inst/ (e.g. inst/figures), and use roxygen2 to generate the Rd files and \usage rather than hand-written ones. | 47 | 2% | 3% | 2% |
| 16 | Keep example and Rd lines within 80 columns (100 at most), with consistent formatting and spacing. Edit the roxygen source rather than hand-wrapping the generated Rd. | 37 | 2% | 0% | 2% |
| 17 | Give each man page a short, distinct title written as a noun phrase, and do not copy the description text into the title. | 24 | 1% | 0% | 1% |
| 18 | Remove template or skeleton leftovers from Rd files: placeholder keywords, TODO/TBA text, empty sections, empty \references, and comment-only examples sections. | 24 | 1% | 0% | 1% |
| 19 | Remove static version, date and license information from package man pages, and give Bioconductor installation instructions via BiocManager in the README. | 21 | 1% | 1% | 1% |
| – | _unmatched points_ | 50 | | | |

Typical wording:

- 1. “Maybe the package help page could use a little more detail and/or link to how to get started using the package?”
- 1. “Consider adding a package help page (accessible via `?scafari`)”
- 2. “Set the defaults `refPvalColumn` and `featImpColumns` to be the ones you are grepping for i.e., `adjpval`”
- 2. “In this case, p.adjust, I think it can be made easier for the user by giving him the available options.”
- 3. “All man pages should have an runnable examples.”
- 3. “Vignette/help doc should have real runable code for `build_gp_links`”
- 4. “We require that your functions are evaluated at least once in either the vignette or the man pages”
- 4. “Every man page should have an example. `findDMPsArray` missing an example. Avoid using donttest / dontrun.”
- 5. “Undocumented data sets: ‘GO’ ‘MSigDB_Hallmark’ ‘SCSE_Result_EMT’”
- 5. “Data in the `data/` directory needs to have a man page for documentation.”
- 6. “the correct syntax is `\code{\link[package]{function}}`”
- 6. “The \description section in `?runibic` repeats the same sentence twice.”
- 7. “It seems like getNB and getFC are wrappers around getting predefined data - this should be better explained.”
- 7. “I suggest expanding the functions documentation to explain how quantities shown in the plots are calculated”
- 8. “Update examples to use `ExperimentHub` in `R/geomx_import_data.R`.”
- 8. “There needs to be a `pdf()` or something similar somewhere in the code if you want to use the `dev.off()`.”
- 9. “the nature of the annotations added to the MATS data.frame should be specified.”
- 9. “The \value should say the function outputs a lists, say how long it is and what the names are.”
- 10. “?run_saint sends users to saint_spc_r()/saint_int_r(), but those functions are internal and have no help pages.”
- 10. “Internal function documentation should contain the tag `@keyword internal`”
- 11. “You are using `if(interactive())` in most of them so they are not tested”
- 11. “Use \donttest instead of \dontrun if you must use this. We recommend writing examples which are fully evaluated.”
- 12. “At the very least the 3 functions should be documented in the same man page.”
- 12. “We would highly recommend reorganizing your R files, but more importantly reorganizing the man files, grouping like or related functions together.”
- 13. “It is unclear why version 6.0 is provided, when version 7.0 is available.”
- 13. “Those about reference papers could be added to the function documentation in `Details` or `Description`.”
- 14. “I'm not sure there's any benefit in wrapping the man page examples in curly braces”
- 14. “The example for this function is also poorly formatted, excessively verbose (e.g., `y=rep(1:5, each=10)`)”
- 15. “The \usage entries for S3 methods should use the \method markup and not their full name.”
- 15. “We don't allow for a figures directory in the man directory. If these figures are needed that they should go in 'inst/figures'.”
- 16. “it would get rid of the NOTE if you shortened your lines. The 80 char limit is part of the style guide in `BiocStyle`.”
- 16. “I noticed the formatting in `?.getAB_edgeR` was a bit weird, you may want to check that”
- 17. “Maybe change the help file title to “MouseData”, or if you want a more human readable title, “Mouse Gastrulation Data”.”
- 17. “The titles of your man page repeat exactly the content of the Description section so are way too long.”
- 18. “contains text that seems like it shouldn't be there”
- 18. “Change all keywords to meaningful keywords or exclude not \keyword{keyword}”
- 19. “You likely don't need to provide a `wget` command for installing your package.”
- 19. “please remove date and version from description. This will be outdated and kept track in DESCRIPTION file”

## code_style

_indentation, line length, naming, formatting, commented-out code_

| # | Item | reviews | first | new | legacy |
|---|---|---|---|---|---|
| 1 | Wrap all code lines to 80 characters or fewer in R/, man/, vignettes, NAMESPACE, DESCRIPTION, README, and roxygen comments (long URLs may stay unwrapped). | 270 | 17% | 3% | 19% |
| 2 | Remove commented-out code, dead code, unreachable code, unused variables and unused functions from R, C/C++, vignette and man files (keep only explanatory comments), and resolve or remove TODO/FIXME comments. | 250 | 15% | 15% | 15% |
| 3 | Indent code with multiples of 4 spaces, using consistent indentation throughout R, C/C++ and Rd files; indent continuation lines of multi-line calls by 4 spaces rather than aligning to the opening parenthesis. | 233 | 15% | 5% | 16% |
| 4 | Use one consistent naming convention (camelCase or snake_case) for functions, arguments, variables and classes; avoid dots in function names to prevent confusion with S3 methods, and start S4 class names with a capital letter. | 200 | 12% | 8% | 13% |
| 5 | Refactor repeated or near-duplicate code blocks and near-identical functions into shared helper functions, or merge them into one parameterised function (e.g. with a method or type argument). | 184 | 11% | 15% | 11% |
| 6 | Reformat the code with styler or formatR (or follow the Bioconductor coding style guide) for consistent spacing around operators, a space after commas, braces and if/else layout, and consistent indentation. | 169 | 10% | 5% | 11% |
| 7 | Use <- instead of = (or ->) for assignment in R code, vignettes, man page examples and tests, with spaces around the operator. | 166 | 10% | 5% | 10% |
| 8 | Use descriptive, unabbreviated names for functions, arguments, variables and data objects instead of single letters, acronyms, cryptic or vague names (e.g. use verbs for functions, such as plotX for plotting functions). | 123 | 7% | 2% | 7% |
| 9 | Reduce deeply nested function calls, conditionals and loops by using intermediate named variables, sequential statements, a switch, or combined conditions, and put pipe steps on separate lines. | 88 | 5% | 3% | 5% |
| 10 | Split long functions (over about 50 lines) and monolithic functions into smaller, single-purpose helper functions, and reduce cyclomatic complexity. | 86 | 5% | 13% | 4% |
| 11 | Organise R source files sensibly: split very large files, group related functions together, name files after the functions or classes they contain, put S4 classes and generics in AllClasses.R and AllGenerics.R, and keep file naming and extension (.R) consistent. | 71 | 4% | 2% | 4% |
| 12 | Move nested function definitions out of their parent functions into top-level internal helpers, and prefix non-exported functions with a dot. | 49 | 3% | 4% | 3% |
| 13 | Remove semicolons used as statement terminators or separators and put each statement on its own line; avoid one-line if statements and always use braces and multi-line blocks for if/else/for. | 34 | 2% | 1% | 2% |
| 14 | Replace tab characters with spaces, and do not mix tabs and spaces in R, vignette or src files. | 31 | 2% | 0% | 2% |
| 15 | Omit unnecessary return() calls, redundant comparisons (== TRUE, == FALSE), redundant ::/::: qualifiers inside the package, and avoid ::: for internal functions. | 27 | 2% | 4% | 1% |
| 16 | Replace magic numbers and hard-coded values with named variables or documented constants, and explain complicated code with comments. | 23 | 1% | 1% | 2% |
| 17 | Do not reuse base or stats function names (c, t, list, scale, which, dir, filter, smooth, etc.) as names of objects or arguments. | 21 | 1% | 0% | 1% |
| 18 | Use message() (or warning/stop) instead of cat() or print() for user output outside show methods; fix typos and avoid all-caps or exclamation marks in messages. | 20 | 1% | 1% | 1% |
| 19 | Use vectorised code or apply-family functions in place of loops that grow objects, and use any()/all() or scalar || and && in if conditions. | 20 | 1% | 1% | 1% |
| 20 | Fix 'no visible binding for global variable/function' notes by properly defining variables, using the .data pronoun or quoted column names, or declaring globalVariables. | 19 | 1% | 1% | 1% |
| 21 | Separate computation from plotting by providing distinct analysis and plotting functions, and merge near-duplicate plotting functions into one with a type argument. | 16 | 1% | 1% | 1% |
| – | _unmatched points_ | 41 | | | |

Typical wording:

- 1. “Consider shorter lines, 215 lines are > 80 characters long.”
- 1. “Consider shorter lines; 239 lines (10%) are > 80 characters long.”
- 2. “> Commenting TODO’s should be avoided in published package code”
- 2. “commented out code ('dead code') should be removed, e.g., in `R/bioplanet.R`”
- 3. “consider multiples of 4 spaces for line indents. There are 86 lines that are not.”
- 3. “Use proper indentation (again, this also applies to the `Usage` section of your man pages).”
- 4. “Re-name read.pcl and write.pcl to have underscores so they are consistent with the other function names.”
- 4. “Reconsider naming conventions with `.` in the function name; this confuses your plain-old-functions with S3 methods.”
- 5. “You could construct the overlapping DF first and then apply the additional columns in the conditional only.”
- 5. “Very little difference between functions, could probably be reused.”
- 6. “Follow standard code formatting conventions, such as those seen when the code is viewed in R or suggested by packages such as [styler][] or [formatR][]”
- 6. “You may want to look at the [tidyverse style guide](https://style.tidyverse.org/) or the `styler` package.”
- 7. “Please use `<-` instead of `=` for assignment everywhere, in particular in the examples in the man pages.”
- 7. “Avoid using '=' for assignment and use '<-' instead”
- 8. “the name of the argument of the accessor shouldn't try to encode the type of object either so should be `x` or `object`.”
- 8. “Please use arguments that are not abbreviated. For example, use `readLength` instead of `rl`.”
- 9. “for readability of code, it is better to adopt less nesting”
- 9. “It is quite difficult to read a do.call with an lapply inside, consider separating”
- 10. “The recommended function length is 50 lines, 85 functions currently Exceed this.”
- 10. “No excessively long functions. (`selexprep_detect` ~180 lines, `selexprep_qc` ~130, `run_selexprep` ~110, `.extract_selexprep` ~100)”
- 11. “*AllGenerics.R* currently contains a lot more than only generics; please split helpers and methods into (a) separate script(s)”
- 11. “Rename `R/zzz.R` to a descriptive name (e.g., `initialization.R`)”
- 12. “Try to write smaller unexported functions started with "." in the function name, and write the final function as a wrapper for smaller unexported functions.”
- 12. “avoid nesting functions inside functions if they are going to be used once. If these are meant to be helper functions, keep them outside the function and use an naming scheme such as: `.functionName`”
- 13. “No need to use `;`. You can include the code on another line and make it more readable.”
- 13. “adopt a more line-oriented formatting convention for increased readability”
- 14. “consider 4 spaces instead of tabs. There are 6 lines that contain tabs.”
- 14. “Consider 4 spaces instead of tabs; 1911 lines (69%) contain tabs.”
- 15. “the arguments within the function definition could be only taking default values, as you used in `mlmc.R` and `mlmm.R`. `npred`, `np`... are not pred-defined values here, right?”
- 15. “no need to prefix `ExperimentSubset::` here, or `methods::` later.”
- 16. “Could you please add a comment to explain why `tol` is set to this value?”
- 16. “Why not use `"numeric"` or `"double"` instead of `"real"` for consistency with the names of the atomic types in base R?”
- 17. “Since the `plotWidget` function is already taken by the `plotwidgets` package I would recommend to rename it.”
- 17. “base functions such as `c` and `t` are used as variable names. This makes things somewhat difficult to read”
- 18. “Use consistent delimiters in a error message (e.g., in `which.colMax` : `'x'`)”
- 18. “Important: Using `stop()` instead of std::runtime_error”
- 19. “I find this 'compact' representation difficult to read and urge a more standard representation”
- 19. “Vectorize: `for` loops present, try to replace them by `*apply` funcitons.”
- 20. “It is not good practice to set global variables. Please explain why you think you need this and I will suggest an alternative.”
- 20. “R CMD CHECK returns multiple notes like `no visible binding for global variable ‘gid1’`.”
- 21. “repetition in `plotSNRHistogram`, `plotSpatialSNR`, and `plotTICSpatial`”
- 21. “You may have to separate analysis, and plotting functions in `mbqnPlotAll`”

## DESCRIPTION

_DESCRIPTION file fields: Title, Description, Authors@R, biocViews, version, License, URL/BugReports_

| # | Item | reviews | first | new | legacy |
|---|---|---|---|---|---|
| 1 | Declare the minimum R version in Depends as R (>= x.y.z) to match the current Bioconductor release or devel requirement (for example 4.5.0 for release, 4.6.0 for devel). Use valid `>=` syntax and keep README text consistent. | 246 | 16% | 11% | 16% |
| 2 | Add a BugReports field pointing to the package's issue tracker (for example the GitHub issues page), as a single valid URL. | 222 | 15% | 5% | 16% |
| 3 | Remove the `LazyData: true` field from DESCRIPTION, or set it to false. Keep it only with a clear justification, such as a data package with small datasets. | 208 | 14% | 2% | 15% |
| 4 | Expand the Description field into a full paragraph of at least three complete sentences. It should read like a paper abstract, saying what the package does, the data types and methods involved, what is unique about it, how it differs from similar packages, and who would use it. | 176 | 12% | 4% | 13% |
| 5 | Add biocViews terms from the correct hierarchy, with the 'Software' top-level term where applicable. Use only valid leaf terms with exact spelling and case, at least two terms from a single package type (Software, AnnotationData or ExperimentData), and review and add the terms suggested by BiocCheck or the build report. Remove invalid, non-fitting or overly generic terms. | 160 | 10% | 12% | 10% |
| 6 | Use a single Authors@R field with person() entries and roles. Remove the separate Author and Maintainer fields, and give exactly one maintainer the 'cre' role with a valid email address. | 89 | 5% | 2% | 6% |
| 7 | Remove auto-generated or obsolete fields from DESCRIPTION: Date, Packaged, LazyLoad, Type, Remotes, Repository, Collate, ByteCompile, RoxygenNote, git_url, biarch, StagedInstall, LazyDataCompression and empty fields, and any backup file such as DESCRIPTION~. | 84 | 5% | 4% | 6% |
| 8 | Add a URL field pointing to the source repository, package website or Bioconductor landing page. Check that the link resolves and that the URL and BugReports fields do not still point to another package. | 70 | 5% | 2% | 5% |
| 9 | Wrap the Description, Authors@R, biocViews and similar long fields to at most 80 columns with indented continuation lines. Remove blank lines and stray whitespace, and format the dependency fields (Imports, Suggests) one package per line. | 70 | 5% | 1% | 5% |
| 10 | If the work is grant-supported, add the funder to Authors@R with the 'fnd' role and any grant IDs. Otherwise confirm that no funder applies. | 66 | 4% | 30% | 3% |
| 11 | Make Depends hold only R and the few packages whose symbols users need. Move packages that are used only internally to Imports and packages used only in vignettes, tests or examples to Suggests. Add methods to Imports or Depends when S4 is used. | 63 | 3% | 2% | 4% |
| 12 | Specify a recognised standard license in the License field, with an explicit version where one exists (for example GPL-3, GPL-2, Artistic-2.0, MIT). Do not use unrecognised forms such as 'GPL (>= 3)', academic-only or non-commercial licenses, or dual-license strings. | 56 | 3% | 2% | 3% |
| 13 | Proofread the Description and Title for typos, grammar and punctuation. Define acronyms and unclear terms, and remove boilerplate, hyperlinks, references and claims the package does not implement. | 53 | 3% | 3% | 3% |
| 14 | Make the Title a brief, informative one-line summary in title case. It should not end with a period or just repeat the package name, and it should avoid the package-name prefix, 'R package' or 'Bioconductor', abbreviations, stray quotes and malformed text. | 53 | 3% | 4% | 3% |
| 15 | Declare in DESCRIPTION every package imported in NAMESPACE or used in code, vignettes and man pages, in Imports or Suggests, so NAMESPACE and DESCRIPTION agree. Examples are BiocStyle and the other packages the vignette uses, and utils, stats and methods. | 51 | 3% | 2% | 3% |
| 16 | Add ORCID iDs for the maintainer and other authors via the comment argument of person() in Authors@R, using the bare identifier rather than a full URL. | 48 | 3% | 4% | 3% |
| 17 | Drop '+ file LICENSE' and the license file when a standard license is used. If a license file is kept, as for MIT, make it valid and make it match the License field and the man pages. | 46 | 3% | 1% | 3% |
| 18 | Remove duplicate entries and unused or unnecessary packages across Depends, Imports, Suggests and Enhances. Examples are BiocManager, devtools, remotes and roxygen2, and packages already in Depends. | 35 | 2% | 4% | 2% |
| 19 | Fix other malformed DESCRIPTION content: invalid DCF syntax, unclosed quotes, trailing commas, wrong field names, broken emails, and missing authors, original method authors or contributors, as flagged by the build report. | 26 | 2% | 2% | 2% |
| 20 | Use a valid Bioconductor version number: x.y.z with integers and no leading zeros, starting at 0.99.0 for new packages, with an odd y in devel and an even y in release. Bump z on changes, and keep the version in sync with NEWS. | 18 | 1% | 2% | 1% |
| 21 | Consider the package name and Description against similar packages. Explain how the package relates to or differs from them, and consider renaming if the name is confusing, mixed-case or taken. | 18 | 1% | 0% | 1% |
| 22 | Declare external software in SystemRequirements (for example Python, Java or C++ toolchain requirements). Remove entries that are unnecessary or recursive. | 15 | 1% | 1% | 1% |
| 23 | Add the correct Bioconductor-specific fields. This means a valid bioctype where applicable (for example 'Software' or 'Book') and a VignetteBuilder: knitr field when knitr vignettes are used. | 13 | 1% | 4% | 0% |
| 24 | Do not pin minimum versions on dependencies unless there is a justified need, and never on base R packages. | 11 | 1% | 1% | 1% |
| – | _unmatched points_ | 21 | | | |

Typical wording:

- 1. “Update R version dependency from 4.3.0 to 4.5.0.”
- 1. “Depends/Imports/Suggests: R should be >= 4.5.0”
- 2. “We strongly encourage including the 'BugReports:' field with the relevant link to Github for reporting Issues.”
- 2. “Consider adding the relevant links to the Github repository, in DESCRIPTION field of `url:`, and `Bug Report:`”
- 3. “Please remove `LazyData: true` we have rarely found it useful and it can slow installation”
- 3. “'LazyData:' should be set to 'false'. It is our experience that when this field is set to 'true' it can slow down the loading of the package”
- 4. “Please provide a more extensive Description: like a paper abstract describing what specific functionality is provided by this package.”
- 4. “Description could use a bit more detail. What does this package do/how is it different from the other package?”
- 5. “Consider adding these automatically suggested biocViews: CancerData, BreastCancerData”
- 5. “Consider adding these automatically suggested biocViews: Coverage”
- 6. “Please remove `Author` and `Maintainer` if you are using `Authors@R`.”
- 6. “Submitters should be under the maintainer field and are considered responsible for the upkeep of the package.”
- 7. “Please Remove the `Date` and `Packaged` fields. These are added automatically when the package is built.”
- 7. “The 'git_url:' is not a necessary field. Instead I would suggest a 'BugReports:' field with the link to the GitHub Issues.”
- 8. “Recommended to add `URL` field, to direct users to source code repositories, e.g., the GitHub repository.”
- 8. “consider adding `URL:` and `BugReport:` fields pointing to”
- 9. “Indentation matters even in the DESCRIPTION file.”
- 9. “Consider listing `Imports:` as one package per line”
- 10. “the `Authors@R:` field is missing a "fnd" role; if the work is supported by a grant, consider adding this to yourself, or otherwise adding the funding individual as an author with that role.”
- 10. “please add a `fnd` role to `Authors@R` with the relevant grant id(s) to trace funding activities. Not required but encouraged.”
- 11. “We would recommend moving dplyr to Depend, since the full set of dplyr functionality is needed by the end user.”
- 11. “There is a call to scales in the vignette but this package is not listed under depends/imports/suggests.”
- 12. “`License` field: please specify the version. (e.g., GPL-3)”
- 12. “The License is unclear (you have to fix a license it can’t be a conditional statement)”
- 13. “First, what is meant by "out of bounds"? You should explain this in the vignette and in the DESCRIPTION.”
- 13. “Typo in DESCRIPTION: experients -> experiments... I'd also suggest revising/having someone proof-read this as it's a bit choppy to read”
- 14. “Malformed Title field: should not end in a period.”
- 14. “Malformed Title field: should not end in a period.”
- 15. “`BiocStyle` must be added to the 'Suggests:' field since it is used in the vignette.”
- 15. “This entire section can be removed. Packages that must be installed are specified in the `DESCRIPTION` file”
- 16. “Consider adding the maintainer's ORCID iD in 'Authors@R' with 'comment=c(ORCID="...")'.”
- 16. “It is recommended to add ORCiDs to the `Authors@R` field”
- 17. “The 'GPL-3' license is a standard license so the LICENSE file isn't needed.”
- 17. “The DESCRIPTION specifies MIT but the LICENCE file provided is GPL - please choose one.”
- 18. “What is the reason for including packages in the `Enhances` field? This is rarely used and maybe they should go in `Suggests` instead.”
- 18. “Imports: `grDevices` and `graphics` are mentioned twice for each.”
- 19. “Add authors to `DESCRIPTION` for any code that you are porting into your package.”
- 19. “There should only be one Depends: etc field”
- 20. “The `NEWS` states v0.99.1, but the `DESCRIPTION` is at v0.99.0. Make sure to update the latter and push version bumps to the local (origin) as well as to Bioc (upstream) branch”
- 20. “I assume that you will increment the version number to trigger a re-build.”
- 21. “Can you make a comment in the `Description` field about how this package relates to `MSstatsTMTPTM`?”
- 21. “Mention if there are other similar packages.”
- 22. “I think `SystemRequirements` should be added to `DESCRIPTION` (e.g., `GNU make`, C++17)?”
- 22. “You should only list system requirements that come from your own package, not from its dependencies.”
- 23. “You are submitting a Software package so this should be the only term present for 'BiocType'.”
- 23. “`BiocType` field. (one of: Software, ExperimentData, Annotation, Workflow, Book)”
- 24. “Some package version dependencies are overkill. You can remove them for the internal packages such as `graphics`, `methods`, `stats`, `utils`, and `grDevices`”
- 24. “`Depends: R (>= 3.5.0)` doesn't seem very reasonable and should be removed”

## S4_classes_reuse

_reuse of Bioconductor classes/methods (SummarizedExperiment, GRanges...), S4 design, accessors, validity_

| # | Item | reviews | first | new | legacy |
|---|---|---|---|---|---|
| 1 | Reuse existing Bioconductor classes (SummarizedExperiment, SingleCellExperiment, GRanges/GRangesList, GeneSet/GeneSetCollection, Biostrings, MultiAssayExperiment, etc.) instead of custom classes or plain data.frame/list/matrix structures; if a new class is needed, justify in writing why core classes cannot represent it, or extend an existing class. | 247 | 14% | 15% | 13% |
| 2 | Replace direct slot access (@ or slot()) with accessor functions or methods in package code, examples, vignettes and tests; use @ only inside the accessors themselves. | 228 | 14% | 12% | 14% |
| 3 | Accept standard Bioconductor containers (SummarizedExperiment, SingleCellExperiment, ExpressionSet, MultiAssayExperiment, GRanges, Biostrings classes, etc.) as function inputs in addition to or instead of matrices, data.frames or file paths, extracting assay/coldata internally; select the assay by an argument (default 1) and check the class with is(). | 192 | 10% | 10% | 10% |
| 4 | Return standard Bioconductor objects (SummarizedExperiment, GRanges/GRangesList, DataFrame, etc.) from functions instead of nested lists, data.table, tibble or plain data.frames; keep functions endomorphic where possible and carry over row/column names, colData, seqinfo and metadata. | 99 | 5% | 4% | 5% |
| 5 | Replace S3 classes, class() attribute assignment, and R6/reference classes with formal S4 classes defined via setClass, with show methods and S4 methods in place of print/summary S3 methods. | 83 | 4% | 4% | 5% |
| 6 | Provide documented getter accessors for the important slots and results of each S4 class (e.g. p-values, data matrices, metadata), so users do not depend on the internal slot layout or on $ / [[ access. | 78 | 4% | 3% | 4% |
| 7 | Provide an exported constructor function named like the class (capitalised class name) that checks its inputs and calls new() with named slots; do not use initialize() methods or expect users to call new() directly. | 62 | 3% | 2% | 3% |
| 8 | Add a concise, informative show method for every class that summarises the contents and points users to accessors, ending with a newline and not printing overwhelming amounts of data. | 60 | 3% | 2% | 3% |
| 9 | Reuse existing generics (BiocGenerics, S4Vectors, GenomicRanges, IRanges, rtracklayer, SummarizedExperiment) such as granges(), coldata, isEmpty, metadata, score, path and the set operations, and avoid redefining or masking them; give new generics specific, uncommon names. | 57 | 3% | 2% | 3% |
| 10 | Store data and metadata in the standard slots of the container (assays, rowData, colData, metadata, altExps, mcols) rather than separate matrices, custom slots or a new subclass; use metadata() only for experiment-level information. | 55 | 2% | 5% | 2% |
| 11 | Use Bioconductor range infrastructure (GenomicRanges, IRanges, findOverlaps, resize, coverage, nearest, seqinfo, GAlignments) instead of hand-written coordinate calculations, and return genomic results as GRanges/GRangesList with proper metadata column types. | 52 | 2% | 0% | 3% |
| 12 | Add validity methods (setValidity / validity=) for each S4 class that check slots, types, dimensions and required names, accumulate all problems in a character vector and return it (return TRUE when valid) instead of calling stop(); move input checks from functions into validity methods or constructors. | 51 | 2% | 3% | 2% |
| 13 | Define S4 generics carefully: restrict dispatch with signature= to the relevant arguments, omit unneeded ellipsis and braces in generic bodies, and use plain functions for single-method generics. | 50 | 3% | 0% | 3% |
| 14 | Follow naming conventions: capitalise S4 class names, avoid underscores and dots, avoid generic names that clash with Bioconductor/base, and use descriptive method and accessor names without redundant get prefixes. | 48 | 3% | 0% | 3% |
| 15 | Validate function arguments with informative errors, including class, allowed values and prerequisite steps, and document input requirements such as orientation (features x samples), dimensions and ordering. | 47 | 2% | 2% | 2% |
| 16 | Prefer simple, compact data structures: avoid deeply nested lists and redundant slots, use typed S4Vectors lists (SimpleList, NumericList) or DataFrame/tibble when appropriate, and use correct slot types. | 47 | 2% | 1% | 2% |
| 17 | Use existing Bioconductor import and parsing functionality (rtracklayer::import, readGAlignments, Biostrings readDNAStringSet, GSEABase, scanVcfParam) instead of custom BED/GTF/GFF/BAM/FASTA parsers and readers. | 42 | 2% | 3% | 2% |
| 18 | Define methods only for classes the package owns; for foreign classes (matrix, character, Seurat, SummarizedExperiment) use plain functions that dispatch internally on is(), or place methods in the owning package. | 33 | 1% | 2% | 1% |
| 19 | Use is() (methods::is) for class membership tests rather than class() comparisons or custom is.<class> functions, and use S4 dispatch instead of class-based if/else chains. | 33 | 2% | 2% | 2% |
| 20 | Use coercion via setAs/as() instead of custom conversion functions or as.data.frame generics, and offer coercion to/from standard Bioconductor classes. | 33 | 1% | 1% | 1% |
| 21 | Provide setter/replacement methods for user-modifiable slots, defined with setReplaceMethod (e.g. wells(x) <- value), and validate the value on assignment. | 28 | 1% | 1% | 1% |
| 22 | Support the relevant Bioconductor classes in examples, vignettes and example data, e.g. providing example datasets as SummarizedExperiment and showing SummarizedExperiment usage in the vignette. | 23 | 1% | 4% | 1% |
| – | _unmatched points_ | 45 | | | |

Typical wording:

- 1. “Bioconductor has `DataFrame` in S4Vectors for tabular data but SplineDV relies on `data.frame`.”
- 1. “Please use an appropriate Bioconductor class to provide a level of interoperability with other packages (possibly `TreeSummarizedExperiment` still in development)”
- 2. “Avoid using `@` accessors and use established accessors for your class à la `SummarizedExperiment::assay` for example.”
- 2. “avoid direct slot access even in 'internal' code (except of course for accessors, which do not have to be exported)”
- 3. “I'd consider to have `smoothclust()` having separate arguments for input/output assays”
- 3. “`biomarkertmle()` should accept a SummarizedExperiment and extract relevant components inside the function”
- 4. “It says that chipProfile is a GRangesList but the output produced is a regular list - update to GRangesList object.”
- 4. “Many of the exported functions in the package return a `list` or `data.frame` which do not integrate well with the rest of Bioconductor.”
- 5. “Consider using a different name for your `summary` method because the arguments do not match the S3 generic. Also, you're combining systems here with S4 and S3”
- 5. “Consider using S4 rather than S3 objects; the formal class and method definition provide a much more robust environment”
- 6. “exported accessors) and avoid direct `@` slot access on objects from other packages (e.g. `dgCMatrix`).”
- 6. “Please create one general function that will access different parts of the object based on an argument (similar to `SummarizedExperiment::assay`)”
- 7. “when constructing an object it's usually better to process / formulate the arguments and then conclude with a call to `new()`”
- 7. “We don't reccomend using an initialize method. The MBR class should have a constructor and validity”
- 8. “that the derived implementation always starts with `callNextMethod()`.”
- 8. “seems like the print method for the object class should be with”
- 9. “You should be able to import and use this generic for your own purposes.”
- 9. “you may not need to create additional methods for `PCAGenomicSignatures` because they're automatically inherited”
- 10. “Avoid relying on an element in the metadata as the metadata usually does not have a structure or checks and create a more formal slot for the class.”
- 10. “The `metadata` slot of `SummarizedExperiment` is designed as a list to store any type of experiment related meta data”
- 11. “`gmt` would seem to be a perfect candidate for representation as a GRanges object”
- 11. “Please adopt widely used format `chr20:1-57125` instead. One advantage of this format is that it's recognize by the `GRanges()` constructor”
- 12. “Some of these checks are moot since they're already done when the `SummarizedExperiment` is created.”
- 12. “If there are requirements that this list have elements named ... then you need to write a validity method that checks this.”
- 13. “you might be able to reduce the number of methods you need to define and/or you might be able to simplify your methods by making more use of `callNextMethod()`”
- 13. “Your `setGeneric` call for `setRawAssays` are doing too much. They should only register the generic function with the `standardGeneric` call.”
- 14. “It's usually not considered good practice to add the "obj" or "object" suffix to a class name like in `DNEAobj` or `collapsed_DNEAobj`. Please drop the "obj" suffix.”
- 14. “The class name is quite general and we would like 'RNAseq' to refer solely to the method. Please change the name of your data class.”
- 15. “Methods should still validate (e.g., via `stopifnot()`) the remaining arguments.”
- 15. “the data.frame elements have the samples along the rows, rather than the transposed form, that is common in Bioconductor objects?”
- 16. “Nested lists may necessitate an S4 structure to avoid using chain `$` calls”
- 16. “Superficially, it seems (e.g., ddpcrPlate.R:886) that you have implemented a 'list-of-classes' rather than a 'class-of-vectors'”
- 17. “I would suggest to use `Spectra::Spectra()` rather than `MSnbase::readMsData()`.”
- 17. “create_profile.R:64 use `ScanVcfParam()` to selectively import relevant fields from VCF.”
- 18. “it's best not to create methods for classes that you don't own such as 'matrix'”
- 18. “`ExtractCoords()` strikes me as something that would be more cleanly implemented as a generic function with methods for `Seurat`, `SpatialExperiment` and `data.frame` objects.”
- 19. “Since the functions all perform the same operation, implement a generic and methods that dispatch on the class of `object`”
- 19. “Define methods for your class so that you don't need to check for S4 class membership because it will only dispatch to that class”
- 20. “Use standard coercion methods `as(x, "SummarizedExperiment")` rather than a plain function `as_summarized_experiment()`.”
- 20. “or via an appropriately named and prominently available bespoke function in your package”
- 21. “this code looks quite unusual; why is it idfferetn from simply `seqtype(ans) <- seqtype` ?”
- 21. “Should there be any sort of validation for the replacement/setting of”
- 22. “The example data is a plain `list`. You need to demonstrate interoperability with Bioconductor packages and container classes.”
- 22. “There is virtually no integration with other Bioconductor packages. ... What core Bioconductor data structures do you use?”

## NAMESPACE

_NAMESPACE imports/exports, importFrom vs import, exporting too much_

| # | Item | reviews | first | new | legacy |
|---|---|---|---|---|---|
| 1 | Replace whole-package import() directives with selective importFrom() (or roxygen @importFrom) for packages where only a few functions are used; reserve import() for packages heavily used or whose classes/generics are relied upon (e.g. methods, S4Vectors, SummarizedExperiment). | 195 | 13% | 5% | 13% |
| 2 | Do not export internal helpers, dot-prefixed functions, S4 method helpers, or functions used only internally or by a Shiny app; keep them unexported (optionally prefix with a dot or use @keywords internal) and remove their man pages, or justify why they are exported. | 97 | 5% | 6% | 5% |
| 3 | Add importFrom() declarations for all functions flagged by R CMD check/BiocCheck as undefined globals or suggested imports, including base-package functions from stats, utils, graphics, grDevices and methods (e.g. importFrom(methods, is, new), stats median/sd, utils head), and declare those packages in Imports. | 94 | 5% | 2% | 5% |
| 4 | Avoid pkg:: calls in package source code for packages not imported in NAMESPACE; import the functions instead and call them unqualified, and recheck imports whenever DESCRIPTION changes so dependency checks are triggered. | 84 | 5% | 8% | 5% |
| 5 | Import every package listed in Depends or Imports in the NAMESPACE (via import/importFrom), and keep DESCRIPTION Imports and NAMESPACE imports in sync: add missing entries, and remove packages that are declared but never used or imported from. | 72 | 4% | 6% | 4% |
| 6 | Rename exported functions to avoid dots (which suggest S3 dispatch), using camelCase or snake_case, and apply one naming convention consistently across all exports. | 51 | 3% | 3% | 3% |
| 7 | Make exported function names descriptive, reasonably short and unique: avoid generic names, names that clash with base/stats/Bioconductor generics, redundant package-name prefixes or suffixes, and names differing only by case; name the main function after the package. | 45 | 3% | 1% | 3% |
| 8 | Generate NAMESPACE with roxygen2 (devtools::document()) with @import/@importFrom/@export tags placed in the source files rather than hand-editing it, and tidy it up: no stray characters, blank lines, commented-out or empty directives, or over-long lines. | 38 | 3% | 1% | 3% |
| 9 | Use S4 generics/methods or existing generics (e.g. plot, show, BiocGenerics) rather than defining new prefixed functions or redefining generics, and register S3/S4 methods correctly in NAMESPACE (S3method, exportMethods, importMethodsFrom for imported generics). | 35 | 2% | 2% | 2% |
| 10 | Move packages to the proper field when appropriate: heavily used or class-defining packages to Depends, packages used only in vignettes/tests (e.g. BiocStyle, testthat) or optional ones to Suggests, and remove unnecessary imports of data/annotation packages. | 28 | 2% | 1% | 2% |
| 11 | Be consistent per package: do not combine import() and importFrom() for the same package, remove redundant importFrom lines when the whole package is imported, and merge multiple importFrom directives for one package into a single line. | 26 | 2% | 3% | 2% |
| 12 | Remove unused imports and verify that each imported or exported symbol is actually used or documented, with a man page for every exported function. | 25 | 1% | 0% | 1% |
| 13 | Do not export or re-export imported functions or operators such as %>% or := ; use the native |> pipe, or import the pipe selectively, and re-export it only if users are expected to use it. | 24 | 1% | 0% | 2% |
| 14 | Replace exportPattern() with explicit export() directives (or @export tags), and export only the functions end users need to call. | 22 | 1% | 0% | 2% |
| 15 | Ensure everything users need is exported: functions used in examples and vignettes, generics and methods (exportMethods/exportClasses/S3method) for exported classes, constructors and accessors, and functions referenced in See Also; the NAMESPACE must not leave users needing :::. | 22 | 1% | 1% | 1% |
| 16 | Do not use ::: to access unexported objects from other packages (including your own package); ask the owner to export the function, use an exported alternative, or justify it. | 15 | 1% | 1% | 1% |
| 17 | Remove library(), require() and requireNamespace() calls from package code and rely on NAMESPACE imports; use requireNamespace() only for Suggests packages. | 14 | 1% | 0% | 1% |
| 18 | Resolve import conflicts and masking warnings on load by importing only the needed symbols or using import(..., except=...), and avoid exports that mask functions from other packages. | 9 | 0% | 0% | 0% |
| 19 | Fix native-code registration: add useDynLib() with .registration=TRUE and a correctly named R_init_<pkg> routine. | 3 | 0% | 0% | 0% |
| – | _unmatched points_ | 21 | | | |

Typical wording:

- 1. “Selectively import the needed functions via `@importFrom` instead of importing the whole package via `@import`.”
- 1. “Strongly recommend just doing `import(BiocGenerics)` and `import(methods)` rather than worrying about importing individual symbols”
- 2. “Should the `organize_inputs()` function be exported at all? It seems tangential to the package core scope”
- 2. “Internal functions are not usually `@export`ed and are only available in the”
- 3. “Consider adding importFrom("grDevices", "colorRampPalette") to your NAMESPACE file.”
- 3. “Consider adding `importFrom("stats", "cor", "p.adjust", "prcomp", "weights")` to your NAMESPACE file.”
- 4. “You may also consider importing some dplyr functions (try `@importFrom` in roxygen2) like `select`, `mutate` etc which you are using commonly instead of calling `dplyr::select` etc each time.”
- 4. “I recommend removing one or two instances of `::` so that dependency checks are triggered automatically.”
- 5. “A package in 'imports' in DESCRIPTION should be fully or selectively imported in NAMESPACE.”
- 5. “'tibble' is being imported but I don't see it listed as an `import()` or `importFrom()` in the NAMESPACE file.”
- 6. “Exported functions should use camel case or underscoring and not include '.' indicate S3 dispatch.”
- 6. “Please be consistent with the use of `camelCase` or `snake_case` for function names”
- 7. “Consider renaming the main function to the name of the package (i.e., `HiBED()`)”
- 7. “The name of the `tRNAscan2GRanges()` function makes it sound like it performs some kind of coercion when it's in fact an I/O function.”
- 8. “its is best to use `@import()` or `@importFrom()` to explicitly declare what symbols from which packages are being used.”
- 8. “There are some lingering windows character in the NAMESPACE (\M) please clean”
- 9. “If you want to import a method then use `@importMethodsFrom` rather than `@importFrom`”
- 9. “`samples()` is a generic that is already defined in the Biobase package so you would need to import Biobase.”
- 10. “There should be no classes exported in the package”
- 10. “I don't think you need to specify AnnotationHub, ExperimentHub will load AnnotationHub for you.”
- 11. “Please pick one or the other, it seems for GenomicFeatures you use both import() and importFrom().”
- 11. “Please remove selective imports for packages in 'Depends' and either fully import or leave them out of the NAMESPACE.”
- 12. “You import `BiocStyle::html_document()` in `R/GXwasR_helper_functions.R:26` but do not use it anywhere in the package”
- 12. “REQUIRED: Namespace in Imports field not imported from: 'ggplot2'. All declared Imports should be used.”
- 13. “It seems like there are many commonly named functions being re-exported. This doesn't seem quite right?”
- 13. “Consider re-exporting the `%>%` if you intend your users to use the”
- 14. “Remove `exportPattern("^[^\\.]")`. Export functions explicityly. Use roxygen.”
- 14. “Explicitly export functions in your package, do not use a pattern for exporting functions”
- 15. “In any case you need to export that method.”
- 15. “Is there a reason why none of the functions in your package are being exported?”
- 16. “Unexported object imported by ':::' calls. You are not allowed to access non-exported functions from other packages.”
- 16. “`ODER:::` (with triple colons) in same package code is rarely needed see `R/ODER.R`.”
- 17. “To accomplish this you library(GenomicRanges) in all examples.”
- 17. “remove `library()` calls; required functions should be imported in the NAMESPACE.”
- 18. “Consider importing the whole package, e.g., the `dplyr` and `stats` here. For conflicting functions, use for example `@rawNamespace import(Utils, except=c(“head”, “tail”))`.”
- 18. “Fix the import of 'gridExtra', you have both `import(gridExtra)` and `import(gridExtra, except = c(combine))`.”
- 19. “consider `useDynLib(SpiecEasi, .registration = TRUE)`”
- 19. “Add useDynLib("GSminer", .registration=TRUE) to NAMESPACE”

## unit_tests

_testthat/RUnit tests and coverage_

| # | Item | reviews | first | new | legacy |
|---|---|---|---|---|---|
| 1 | Write unit tests for all exported functions, and ideally for internal/helper and non-exported functions, so that the main package functionality and core algorithms are exercised. | 185 | 11% | 9% | 12% |
| 2 | Measure coverage with covr (covr::report() or devtools::test_coverage()), then add tests for files and functions with 0% or low coverage and raise overall coverage substantially, aiming for high coverage (e.g. 80-90%) over time. | 153 | 9% | 24% | 8% |
| 3 | Add a tests/ directory with testthat unit tests (tests/testthat.R plus tests/testthat/test-*.R) that run during R CMD check; replace empty, placeholder, trivial or boilerplate test files with real tests, and use testthat or RUnit but not both. | 146 | 10% | 3% | 10% |
| 4 | Make tests check real behaviour: use expect_* assertions on actual returned values, including numerical correctness against known, hand-computed or reference values with a tolerance, not only output class, structure, or that the code runs without error. | 44 | 2% | 3% | 2% |
| 5 | Test error handling and edge cases: invalid or unexpected inputs, missing arguments, all supported input types (e.g. matrix, SummarizedExperiment, SingleCellExperiment), and input validation, using expect_error/expect_warning/expect_message. | 38 | 2% | 3% | 2% |
| 6 | Fix all failing, erroring, or warning-producing tests (including tolerance issues, stale expected messages or values, and missing data files) so R CMD check and devtools::test() pass cleanly; re-enable commented-out or skipped tests, or remove them with justification. | 25 | 1% | 0% | 1% |
| 7 | Remove test files, directories or tests that serve no purpose (empty files, unrelated arithmetic checks, tests that compare deparsed source), or fill them with meaningful tests of the package's own functions. | 22 | 1% | 1% | 1% |
| 8 | Avoid external downloads and system-specific dependencies in tests: use small bundled data (inst/extdata via system.file) or data generated inside the test, and use mocking or recorded fixtures (e.g. httptest2) for remote resources and system tools. | 21 | 1% | 2% | 1% |
| 9 | Do not skip core tests on Bioconductor build machines: remove unjustified skip_on_bioc(), skip_if_offline() and skip_if_not_installed() gates, especially for packages in Imports, and use skip guards only for genuinely optional Suggests packages, credentials or network resources. | 20 | 1% | 9% | 1% |
| 10 | Keep tests free of side effects and clutter: write temporary files to tempdir(), do not leave Rplots.pdf or other artifacts in tests/, use temporary caches instead of the user's real cache, and remove unneeded library() calls, unused or commented-out code, and stray files. | 16 | 1% | 0% | 1% |
| 11 | Structure tests properly: wrap all test code in test_that() blocks with clear descriptive names, keep each block focused on one thing with several expect_* calls where useful, and make blocks independent of each other without shared state or <<- assignments. | 15 | 0% | 2% | 0% |
| 12 | Use specific and current testthat expectations, such as expect_s3_class, expect_type, expect_named and expect_warning, instead of expect_true on class checks, manual if-statements, suppressWarnings, or deprecated expect_is and context(); wrap expected warnings in expect_warning or remove the cause. | 15 | 1% | 3% | 1% |
| 13 | Keep tests fast and light: use small data, define shared test objects once rather than rebuilding them, move long-running tests to the longtests directory, and stay within the check time limits. | 14 | 1% | 2% | 0% |
| 14 | Organise test files under tests/testthat with names mirroring the R source files they test, and make sure tests/ is not excluded in .Rbuildignore. | 13 | 1% | 0% | 1% |
| 15 | Add tests for visual and interactive outputs, such as plots (vdiffr or snapshots) and Shiny apps (shinytest2), and add expectations to any plotting test code whose output is not currently checked. | 12 | 1% | 1% | 1% |
| 16 | Test the package's own logic rather than behaviour of dependencies, and test intermediate stages and smaller helper units instead of only the integrated pipeline; refactor large functions into smaller, testable units. | 11 | 0% | 0% | 0% |
| 17 | Use accessor methods, is(), and exported interfaces in tests instead of @ slot access or class() comparisons. | 4 | 0% | 0% | 0% |
| 18 | Avoid trycatch wrappers that silently hide failures in code and tests, so that coverage and failures are reported accurately. | 2 | 0% | 0% | 0% |
| – | _unmatched points_ | 25 | | | |

Typical wording:

- 1. “Optional: Add more tests to increase the robustness of the package.”
- 1. “Highly recommend unit tests, they are very helpful with package development and maintenance.”
- 2. “Unit test coverage (of non-long tests) is currently at <9% overall, which is fairly minimal given the amount of code in the package”
- 2. “The coverage is alright for now but I would recommend to increase it in the future.”
- 3. “We strongly encourage the use of unit tests.”
- 3. “Add a tests folder to enhance robustness.”
- 4. “Please add assertions on values, such as column names, dimensions, and value ranges.”
- 4. “no real tests in terms of results is done. I'd encourage expanding testing towards assuring that results are "scientifically" accurate and as expected.”
- 5. “Consider adding more tests to ensure code has desired functionality for the user.”
- 5. “Include unit tests to increase robustness.”
- 6. “Failure ('test-plotQueryResults.R:97:5'): plotQueryResultsViolin works ── file.info(tf)["size"] > 20000 is not TRUE”
- 6. “Failure in test coverage for epiregulon.extra ... Snapshot of `testcase` to 'visualization/violin-plot.svg' has changed”
- 7. “any change to these functions makes the test suite fail, including the change needed to fix the WARNING above”
- 7. “None of the unit tests are testing the code in **methylTracer**. Rather, they are boilerplate examples generated by **testthat**.”
- 8. “There was an error in running `covr::package_coverage` but this may have been due to not downloading all 91 resources to my machine.”
- 8. “`test-login.R` currently asserts `"HTTP 500 Internal Server Error."` from a bad-credentials call. That pins a test to a server-side detail”
- 9. “have the tests skipped if there is not a specific directory present”
- 9. “The tests should be runnable without requiring Suggsts packages - use guards to check whether those are installed and skip if not.”
- 10. “The tests seem to generate an Rplots.pdf file in the tests/testthat/ directory.”
- 10. “Then you will get rid of the inst/unitTests directory and the 2 files you have in the tests/ directory (RunTests.R and expected_results.tsv).”
- 11. “the test named `"transferLearning_function"` actually tests `initTransferLearningParamaters()`”
- 11. “it is usually best practice to write self-contained tests”
- 12. “There is some code in the tests file currently by no actual expectation checks”
- 12. “When a warning is expected, please use `expect_warning()` instead, so that unexpected warnings are not hidden.”
- 13. “Many are too complicated for this purpose. Tests should all include `expect_*()` statements resulting from simple and fast computations”
- 13. “The long tests have errors when I try to run them.”
- 14. “The naming for test files should generally match the naming of your `.R` files”
- 14. “I'm not sure I understand what `tests/test-ExperimentSubset.R` is doing here, rather than within `tests/testthat/`?”
- 15. “Consider implementing for *plotting_functions.R*; `devtools::test_coverage()` currently gives:”
- 15. “It does not make sense to include calculations whose output is not tested, e.g., plotting figures.”
- 16. “Effective unit tests often benefit from more modular code, where each module can be tested quickly and with simple inputs and outputs”
- 16. “We strongly encourage **unit tests**; see [here](http://bioconductor.org/developers/how-to/unitTesting-guidelines) for guidelines.”
- 17. “In the tests, avoid using direct slot access with '@' but use an accessor method instead.”
- 17. “To test for S4 class, use the name of the class, e.g., `is(X, "KnownS4Class")`”
- 18. “this is due to the fact that the [function fails silently] and returns `An error occurred: Environment variable 'HAPMAPIII_NCBI36_DIR' is not set”
- 18. “In R, it is more common to do robust input checking and validation, so that no unexpected errors are thrown during execution.”

## data_ExperimentHub

_package data size, inst/extdata, ExperimentHub/AnnotationHub, downloads, data documentation, caching_

| # | Item | reviews | first | new | legacy |
|---|---|---|---|---|---|
| 1 | Document every exported dataset in data/ (and any sysdata objects) with a man page or data.R entry giving description, source/reference URL, how it was created (or simulated), object class, rows/columns and column meanings, with the object name matching the file and help topic name. | 126 | 7% | 4% | 7% |
| 2 | Add a script or README under inst/script (not data-raw) documenting how every file in inst/extdata was generated, including source URLs, filtering/processing steps, and licensing, so users can roughly reproduce it. | 109 | 7% | 9% | 7% |
| 3 | Place data in the correct directory: raw files in inst/extdata (accessed via system.file()), processed/exported objects in data/ (documented and loaded with data()), internal objects in R/sysdata.rda, scripts in inst/script, and nothing in data-raw, inst/testdata, the package root or R/. | 77 | 5% | 4% | 5% |
| 4 | Move large or bulk data to ExperimentHub or AnnotationHub (or a separate experiment data package), with correct metadata.csv fields, S3 upload, distinct titles/descriptions, and rdatapaths; otherwise justify not using a hub. | 57 | 2% | 3% | 2% |
| 5 | Use BiocFileCache (e.g. bfcrpath) to cache all downloaded resources so files are fetched once and persist across sessions, rather than downloading repeatedly, into the working/home/installed directory, or at build time; default to tempdir or a user cache dir if a cache argument is needed. | 56 | 3% | 3% | 3% |
| 6 | Reuse existing Bioconductor data (ExperimentHub, AnnotationHub, experiment/annotation data packages, e.g. pasilla, scRNAseq, GO.db, excluderanges) instead of bundling or duplicating data, or justify why new data is needed. | 45 | 2% | 1% | 2% |
| 7 | Include a readme or man page explaining the contents, origin, format and purpose of each inst/extdata file, and remove or justify files that are unused by examples, vignettes, tests or functions. | 43 | 2% | 5% | 2% |
| 8 | Do not download data from unstable or personal locations (GitHub raw, Google Drive, Dropbox, FTP, Google Sheets, arbitrary websites) in package code, vignettes or examples; ship small data in the package or host on ExperimentHub/AnnotationHub or a stable archive such as Zenodo. | 39 | 2% | 0% | 2% |
| 9 | Provide small, realistic example/toy data (subset of real data or mock data) in the package so examples, vignettes and tests run quickly without large downloads. | 37 | 2% | 4% | 1% |
| 10 | Keep the package within Bioconductor size limits (tarball under 5 MB, individual files at or under 5 MB, and data under about 10 MB) by removing, subsetting or compressing bundled data, and clean large files from git history. | 35 | 2% | 0% | 2% |
| 11 | Remove unused or redundant data files (duplicate datasets, unneeded images, jar files, docx/pdf, duplicate rda/text versions) and avoid saving datasets or files from within functions or examples. | 30 | 1% | 1% | 2% |
| 12 | Give datasets and data objects descriptive, specific names (including study origin where useful) that avoid generic names like 'data' or 'dat', underscores, and clashes with function names. | 22 | 1% | 0% | 1% |
| 13 | Load package data using the standard data() mechanism per ?data good practice and R-pkgs guidance, without custom loader functions, load() of files, .onLoad hooks, or global-environment side effects; handle LazyData appropriately for large data. | 20 | 1% | 0% | 1% |
| 14 | Resave .rda files with better compression (e.g. xz), save one object per file, and fix compression warnings or corrupt data files. | 18 | 1% | 0% | 1% |
| 15 | Confirm licensing and redistribution permission for all bundled or derived data (e.g. KEGG, TarBase, GeneCards, IMGT, restricted data), include attribution, and remove data or provide user download instructions where redistribution is not allowed; cite primary sources. | 18 | 1% | 2% | 1% |
| 16 | Provide instructions or functions for users to download, create or supply their own data (including expected input format), and add a real-data example in addition to simulated data. | 18 | 1% | 5% | 1% |
| 17 | Justify bundled data and package structure: explain why a separate data package is or isn't needed, avoid maintaining data packages solely for examples, and remove the ExperimentHub biocView unless the package is a true hub package. | 16 | 1% | 1% | 1% |
| 18 | Use appropriate data structures and types: Bioconductor classes (SummarizedExperiment, SingleCellExperiment) where suitable, matrices for counts, atomic vectors, correct column types (integer, numeric, factor), NA for missing values, and meaningful row/column names. | 14 | 1% | 1% | 1% |
| 19 | Ensure data-generation scripts are reproducible: no machine-specific paths, correct input/output paths, source URLs included, and generated objects consistent with the script. | 13 | 1% | 4% | 0% |
| 20 | Document accurate genome and metadata information in data objects (reference genome, seqinfo/seqlengths, assembly version) and make documented values (row counts, names, sources) consistent with actual data. | 9 | 0% | 1% | 0% |
| 21 | Fetch Java/jar or other external resources via a cache or data package rather than shipping or downloading them at build time from third-party sites. | 2 | 0% | 0% | 0% |
| – | _unmatched points_ | 3 | | | |

Typical wording:

- 1. “A source url should be provided for this data as well.”
- 1. “The actual provenance of the count data is not provided. Is it derived from GEO, SRA?”
- 2. “It should include source URLs and any key information regarding filtering or processing.”
- 2. “Please add scripts about how to generate the example data in `extdata` folder”
- 3. “Why not make it directly a data.frame available as data in the `data/` folder (as, for example, with the example datasets)?”
- 3. “There is an additional `R/sysdata.rda` data file. This should either be removed or moved to the `data/` or `inst/data` directories.”
- 4. “if the data is more than 50Mb, then the data should preferrably be hosted on ExperimentHub”
- 4. “You'll want to have some distiction between the title and description for”
- 5. “The package should cache files. Bioconductor recommends `BiocFileCache`.”
- 5. “BiocFileCache should be implemented also around getLink or in the functions that call this method.”
- 6. “Was there no existing package that could provide this example data on `ExperimentHub`?”
- 6. “Your package will also need to be redesigned to leverage databases already in Bioconductor rather than relying on various supplementary files from your research group's server.”
- 7. “What is this? document it with a man page on where it came from.”
- 7. “Please add documentation of any `inst/extdata` (e.g., source information under a `?data` page, and/or `inst/scripts` code for how the data were generated)”
- 8. “Downloads of files and external data from the web should be avoided.”
- 8. “Avoid direct download of resources (e.g., from the Broad) within the vignette and even package code (if any).”
- 9. “could you ship them as a small example dataset (ideally as a `SummarizedExperiment`, with the script generating it in `inst/scripts/`)”
- 9. “Provide a small dummy set of data that will run in the time constraints.”
- 10. “the data provided with the package is rather large (31M); package generally have to be <4M. Can you provide a small subset to run with the vignette?”
- 10. “Size of individual files <= 5MB. * installed size is 30.0Mb ... extdata 28.4Mb”
- 11. “I saw that you have multiple `*.png` files in the package. Do you need to include all of those?”
- 11. “If the other datasets aren't used (or demonstrated) then they shouldn't be included.”
- 12. “Some datasets need more descriptive names, "*_example" is not very helpful.”
- 12. “Don't call your data set "data". This is way to generic.”
- 13. “The `AnnotationHub` query is not necessary when you already have a data package that has a covenience function for loading the data.”
- 13. “loading should be through the standard mechanism. Having the files in data/ makes them visible via a call to data()”
- 14. “the data format should not be serialized R objects, but rather flat files that can be easily accessed according to FAIR principles”
- 14. “dgMMirGraph.rda needs to be compressed. See the warning on R CMD check.”
- 15. “Redistributing content of KEGG pathway databases is not allowed. Use KEGGREST to acquire pathway”
- 15. “One possibility is to provide the user with instructions for downloading the data to their own computer, independently of your package.”
- 16. “Data loading section just loads an RDS file without explanation of expected format. Please show how to import actual data into R.”
- 16. “Important: Consider adding instructions for download or creation for the extra data.”
- 17. “Your `loadDataset()` utility function belongs to the data package. You don't need to export it”
- 17. “Is all this necessary since you uploaded data in the hub?”
- 18. “Don't call a sample an "observation" as this is kind of vague”
- 18. “Update to use a Bioconductor formated object.”
- 19. “Consider including a script that generated the dataset documented in `data.R`”
- 19. “I'm unable to run `inst/scripts/make-data.R` since it loads a number of files from the non-existent `raw` directory”
- 20. “The first file `DataLoad.R` involves too much hard coding of chr and values. Please interoperate with other bioconductor packages and avoid this.”
- 20. “the genome information seems to be incorrectly stored”
- 21. “Ideally, the java source code and / or jar files would be incorporated into your package or an 'experiment data' package.”

## dependencies

_Depends/Imports/Suggests choices, heavy or non-CRAN/Bioc deps, system requirements_

| # | Item | reviews | first | new | legacy |
|---|---|---|---|---|---|
| 1 | Move packages used only in vignettes, examples, tests, or optional or non-core functions (plotting, Shiny, annotation, Seurat and similar heavy packages) from Imports or Depends to Suggests. This includes knitr, rmarkdown and BiocStyle. Call them with the `::` prefix. | 60 | 3% | 5% | 3% |
| 2 | Replace convenience dependencies with base R or lighter equivalents. This covers magrittr (use the native pipe |>), dplyr, tidyr, stringr, plyr, reshape2, purrr, forcats, tibble, glue, data.table, assertthat, RColorBrewer, fs and tidyverse. Do not import tidyverse as a whole. | 59 | 4% | 6% | 3% |
| 3 | Remove packages from Imports, Depends and Suggests that the code, vignettes, examples or tests never use. Check that every listed package is actually needed, and drop leftovers such as devtools, BiocCheck, testthat, biocViews, sessioninfo or BiocGenerics. | 57 | 3% | 8% | 2% |
| 4 | Declare every package the code, vignette or tests use in the correct DESCRIPTION field. This includes packages called with `::`, library() or require(), packages whose generics or functions are imported in NAMESPACE, and data or annotation packages used in examples or vignettes. Keep DESCRIPTION Imports and the NAMESPACE import directives in sync. | 54 | 3% | 6% | 2% |
| 5 | Reuse existing Bioconductor infrastructure instead of reimplementing it. Examples: rtracklayer or BiocIO for import/export, GenomicRanges, Biostrings instead of seqinr, Rsamtools instead of system samtools, KEGGREST, GSEABase, matrixStats or MatrixGenerics, tximport, and org.*.db or AnnotationHub. | 41 | 2% | 4% | 2% |
| 6 | Keep Depends minimal. Move packages to Imports (with NAMESPACE imports) when they only support internal code, when users don't need their functions attached, or when they are data or build-only packages. Do not list a package in more than one of Depends, Imports, Suggests and Enhances. | 40 | 2% | 1% | 2% |
| 7 | Reduce the total number of dependencies (direct and indirect) to limit fragility and load time. Drop packages used for only one or a few functions, replacing them with base R or existing Bioconductor infrastructure, and consider splitting the package or running pkgndep to find heavy parents. | 39 | 2% | 4% | 2% |
| 8 | Guard every Suggests package before use with requireNamespace() (or BiocBaseUtils::checkInstalled), ideally at the start of the function. Fail with a clear install message or skip optional functionality. Do not require Suggests packages for examples to run, and do not use library()/require() inside package code. | 28 | 1% | 3% | 1% |
| 9 | Make all dependencies available from CRAN or Bioconductor. Remove GitHub-only, removed-from-CRAN or orphaned packages from DESCRIPTION, code and vignettes, or submit them to Bioconductor. Do not advise installing from GitHub. | 24 | 1% | 5% | 1% |
| 10 | Justify or avoid heavy or questionable dependencies. Examples: data.table, Seurat, gmapR (fails on Windows), ggplot2 in infrastructure packages, and licence-problematic packages such as akima. Prefer packages in the Bioconductor ecosystem, and make Bioconductor-integrating classes (SummarizedExperiment, SingleCellExperiment) the core. | 24 | 1% | 4% | 1% |
| 11 | Put a package in Depends only when users need its classes or generics attached. Examples are SummarizedExperiment, GenomicRanges, SingleCellExperiment, MultiAssayExperiment, flowCore, or methods that operate on your objects. Otherwise import it properly instead of relying on it implicitly. | 23 | 1% | 1% | 1% |
| 12 | Declare data packages used by the software, vignettes or tests (experiment data, annotation, BSgenome) in the proper field. Keep the data package's Depends only in the data package, and keep only the genome packages the vignette needs. | 22 | 1% | 2% | 1% |
| 13 | Move packages that the code needs unconditionally from Suggests to Imports, or guard their use. Examples include matrixStats, BiocParallel, Rsamtools, DESeq2 and upsetR. | 20 | 1% | 4% | 1% |
| 14 | Use BiocParallel instead of parallel, doParallel, foreach, snow, snowfall or custom parallel code. Declare it in Imports and NAMESPACE. | 19 | 1% | 1% | 1% |
| 15 | Declare required external software (kallisto, perl, tensorflow, cwltool, conda and similar) in SystemRequirements, and remove entries the code doesn't need (GNU make without a Makevars, Cytoscape, ShortStack). Justify system dependencies, avoid system()/system2 calls to external tools in favour of R or Bioconductor functions, and make any remaining calls portable. | 19 | 1% | 0% | 1% |
| 16 | Resolve dependency-related build and check problems. Examples: installation failures from unavailable or Java/Boost-dependent packages, generic masking conflicts, missing-package warnings or notes, and unavailable maintainers or abandoned upstream packages. | 18 | 1% | 0% | 1% |
| 17 | Use basilisk (or reticulate) to provision and run Python dependencies in a defined environment. Declare the required module versions there, avoid ad hoc conda or pip installs, and make sure modules can be supplied as binaries. | 16 | 1% | 1% | 1% |
| 18 | Use the correct tools for web, API and file access. Examples: httr/httr2 or curl instead of RCurl, download.file or rjson; xml2 instead of XML; tools::R_user_dir instead of rappdirs; readxl; rlang `.data` imported via @importFrom with rlang in Imports. | 16 | 1% | 0% | 1% |
| 19 | Drop unneeded version pins and minimum-version constraints in DESCRIPTION. Set the R version dependency to a current release (for example R >= 4.4) or maintain a legacy branch for older R. | 13 | 1% | 0% | 1% |
| 20 | Do not add runtime install checks for packages in Imports or Depends, and do not check for base packages such as parallel. Do not call BiocManager::install(), install.packages() or py_install() from package code, and do not install dependencies automatically. | 12 | 1% | 3% | 1% |
| 21 | Use BiocFileCache for downloading and caching remote or large files, and replace custom caching or retry code. Make functions robust when an external web service is unavailable. | 10 | 1% | 0% | 1% |
| 22 | Do not use unexported functions via `:::`. Avoid `::` throughout the code unless the package is declared and imported, and import the functions you use instead. | 7 | 0% | 0% | 1% |
| – | _unmatched points_ | 2 | | | |

Typical wording:

- 1. “I would suggest keeping the analysis in `Imports`, using base R for file I/O, and moving the interactive layer to `Suggests`”
- 1. “packages that you only use in the vignettes or examples (e.g. `BiocManager`) should be in `Suggests` rather than `Depends`.”
- 2. “I'd strongly suggest removing {dplyr} as a dependency.”
- 2. “What's being called from `stringr` is pretty straightforward with `gsub` and `strsplit`...”
- 3. “the package does not seem to use anything from the **stringr** package so that dependency is not needed.”
- 3. “please remove `base` from `Imports` (it is always available);”
- 4. “All dependencies must be on CRAN or Bioconductor. The `airway` package is needed but is unavailable and unspecified in the DESCRIPTION.”
- 4. “Add `Biobase` dependency to the `DESCRIPTION` when using functions like `exprs` and `pData`.”
- 5. “This needs to be replaced by `pileup` from [Rsamtools](https://bioconductor.org/packages/Rsamtools).”
- 5. “If you think the calls are not reliable enough, you should consider an alternative to `biomaRt`.”
- 6. “If a package provides functionality that a user will use, then include as Depends:, but if the package is needed only for use by your package use `Imports:`”
- 6. “Package listed in more than one of Depends, Imports, Suggests, Enhances: 'Rsubread'”
- 7. “The large number of dependencies makes this package very difficult to maintain.”
- 7. “The list of `Imports` is quite extensive. Is it possible to reduce that number?”
- 8. “use `requireNamespace("RANN", quietly = TRUE)`, and check it once at the top of `sbivarSingle()` / `sbivarMulti()`”
- 8. “this would also help to not require users to install various `Suggests:` to run examples”
- 9. “All dependencies must be on CRAN or Bioconductor”
- 9. “The vignette loads `GOAnno4Bioc`, which is installed from GitHub and is not on CRAN or Bioconductor (we searched both).”
- 10. “There are some licensing issues with the **{akima}** package that make it difficult to use as a dependency.”
- 10. “it is not really clear why `data.table` is used or needed for user-facing data.”
- 11. “you may consider placing it in `Depends:` instead of `Imports:` in your package description.”
- 11. “Include packages such as `shiny` in the `Depends` field since you use the functions in the package extensively.”
- 12. “If you plan on including this package with your submission please, add it accordingly.”
- 12. “`IlluminaHumanMethylation450kanno.ilmn12.hg19` is missing from Suggests”
- 13. “anndataR, stringr, scuttle (+ maybe others) are in `Suggests` but are used unconditionally in the package core code.”
- 13. “kinship2 should be moved to Imports or Depends and imported in the NAMESPACE.”
- 14. “Use the package `BiocParallel` instead of `parallel`.”
- 14. “Use the package 'BiocParallel' instead of the `parallel` package.”
- 15. “**List Perl** in the `SystemRequirements` field in your DESCRIPTION file.”
- 15. “Which all of these dependencies should be listed as SystemDependencies in your DESCRIPTION and not left as an after thought in the man files.”
- 16. “I cannot get pqsfinder to install due to configuration issues with boost.”
- 16. “If you really want to use that data set in your vignette, you might want to try to contact the maintainers yourself”
- 17. “Why not make full use of **reticulate** and use it to install the Python modules”
- 17. “Perhaps adopt a strategy consistent with Bioconductor Python guidance (e.g. basilisk)”
- 18. “Can this be limited to just 'read only' permissions?”
- 18. “Consider using more modern readers such as `readxl`.”
- 19. “Are the versions specified in the `Imports:` field really required? It may be a little too restrictive.”
- 19. “Update R version dependency from 4.3.0 to 4.4.0.”
- 20. “There are individual package installation instructions. All dependencies should only be in DESCRIPTION file.”
- 20. “A check is necessary only for `Suggests` dependencies.”
- 21. “Consider using [BiocFileCache][1] so that both your user and the build system only download large files once.”
- 21. “it must cache the files it downloads, preferably using [**BiocFileCache**](https://bioconductor.org/packages/BiocFileCache/)”
- 22. “If using `%>%`, import from **magrittr** rather than **dplyr**.”
- 22. “`::` is not suggested in source code unless you can make sure all the packages are imported.”

## process

_submission process: version bumps, pushing to git.bioconductor.org, webhooks, SSH keys, how to respond, timelines_

| # | Item | reviews | first | new | legacy |
|---|---|---|---|---|---|
| 1 | Keep the GitHub and Bioconductor git repositories in sync by following the git.bioconductor.org new-package and sync workflow documentation. Push changes to the Bioconductor remote (biocstaging or the devel branch) as well as to GitHub, and pull core-team changes rather than overwriting them. | 115 | 0% | 3% | 0% |
| 2 | Bump the package version in DESCRIPTION (the z part, e.g. 0.99.1 to 0.99.2) with every set of changes, and push it to git.bioconductor.org so a new build is triggered. Pushing without a version bump produces no new build. | 110 | 5% | 11% | 5% |
| 3 | Add an SSH public key to the maintainer's GitHub account and submit it to Bioconductor through the bioccredentials site so pushes to git.bioconductor.org work. If a push fails, check the username and package access on bioccredentials. | 104 | 0% | 0% | 0% |
| 4 | After pushing changes, comment on the submission issue summarizing what was changed and ask for re-review. Do this once the new build report is available and the build is clean. | 63 | 3% | 1% | 4% |
| 5 | Respond point by point (line by line) to each review comment. State what was done, justify any item not addressed, and link or show the code changes. Address earlier open feedback as well, and use the same issue thread rather than starting a new one. | 51 | 2% | 3% | 2% |
| 6 | After the package is added, check the nightly devel build results and status pages to confirm it builds. Do not assume it is available or installable before it appears in the next devel build. | 40 | 0% | 0% | 0% |
| 7 | Reduce the git repository size to below about 5 MB by purging large files from git history with BFG Repo-Cleaner or equivalent. Run gc, check .git size before and after, and push the rewritten history. Removing the files from the current tree is not enough. | 20 | 1% | 1% | 1% |
| 8 | Remove build products, generated files and system files from git tracking: build/, inst/doc/, vignette HTML, tarballs, .Rproj, .Rhistory, .DS_Store, .o files and PDFs. Add them to .gitignore, keeping a single top-level .gitignore. | 19 | 1% | 1% | 1% |
| 9 | Subscribe the maintainer to the bioc-devel mailing list, confirming the mailman acknowledgement so the subscription takes effect. Also register at the Bioconductor support site with the maintainer email, and add the package to the support site watched tags. | 17 | 0% | 1% | 0% |
| 10 | Confirm the build webhook is set up and initialized for the package repository so version bumps trigger builds and build reports appear. If the webhook is not wanted, request a manual build instead. | 17 | 1% | 1% | 1% |
| 11 | Keep the master/default branch limited to package material. Remove or justify extra directories and files such as docs, dev, misc, pkgdown config, Docker files, flake files and unrelated data, or move them to a separate branch or repository. | 16 | 1% | 0% | 1% |
| 12 | Direct further questions to the bioc-devel mailing list or community Slack when the issue will no longer be monitored (closed or accepted). Ask design or advice questions there rather than in the review thread. | 13 | 0% | 0% | 0% |
| 13 | Read the Bioconductor contribution guidelines, developer documentation and release cycle documentation before submitting or resubmitting. Meet release deadlines, or target the next release if the package misses the current one. | 11 | 0% | 0% | 0% |
| 14 | Fix build report errors, warnings and notes before asking for further review, and make sure the package has a runnable example. Test fixes locally before relying on the builders. | 10 | 0% | 0% | 0% |
| 15 | For related packages, such as companion data or client packages, submit them as additional packages in the same submission issue using an AdditionalPackage line. Bump the version of each so each gets a build report. | 8 | 0% | 0% | 0% |
| 16 | Develop and test against R-devel and the current Bioconductor devel version, as the guidelines require, not the release or end-user installation. Use Bioconductor installation methods (BiocManager) rather than devtools::install(), and check with BiocManager::valid(). | 8 | 0% | 0% | 0% |
| 17 | Do not publish the same package on both CRAN and Bioconductor. If it is on CRAN, ask the CRAN maintainers to remove it, remove CRAN badges, and do not advertise it as installable from Bioconductor before acceptance. | 7 | 0% | 0% | 0% |
| 18 | Respond to reviewers in a timely way, within about 2-3 weeks. If more time is needed, say so, so the issue can be paused and reopened later instead of being closed. | 6 | 0% | 0% | 0% |
| 19 | Confirm the long-term maintenance commitment: tick each submission checkbox and keep the original submission template intact. Have all maintainers and authors confirm that inclusion in Bioconductor is acceptable. | 6 | 0% | 1% | 0% |
| 20 | Use informative git commit messages instead of generic ones such as 'commit'. Make meaningful, separate commits (e.g. keep formatting changes apart from functional changes) so authorship and review are traceable. | 5 | 0% | 1% | 0% |
| 21 | Disclose any AI/LLM assistance in the package in the submission issue, commit to maintaining generated code, and write review responses yourself. Clearly label any LLM-generated text. | 4 | 0% | 2% | 0% |
| 22 | Rename the package or repository if needed, for example when the name conflicts or the GitHub name does not match the package. Update the issue URL and the git.bioconductor.org name to match. | 4 | 0% | 0% | 0% |
| – | _unmatched points_ | 32 | | | |

Typical wording:

- 1. “Please make sure that your workflow pulls these changes back rather than overwriting them”
- 1. “The canonical version of your package will be in svn not git hub; encouraging retrieval from git hub means the user may not get the most recent version.”
- 2. “please remember to do a version bump and push to git.bioconductor.org to trigger a new build report.”
- 2. “Remember to bump your version to trigger a re-build.”
- 3. “you can check your username and package access at [BiocCredentials](https://git.bioconductor.org/BiocCredentials/login/).”
- 4. “Please also comment with what has been addressed or answers to the questions above when requesting the re-review.”
- 4. “Comment back here with updates that have been made and when the package is ready for a re-review.”
- 5. “Could you please write a point-by-point response to my initial review so I know what to check in a re-review?”
- 5. “As soon as you have a clean build report, please include a detailed response of each point.”
- 6. “if the webhook is initialized then a new build report will be generated on a version bump in the DESCRIPTION file”
- 7. “Your repository is 12MB and we want to see repositories smaller than 5MB.”
- 7. “Some objects in your git history exceed the allowed 5MB size limit. Please remove them.”
- 8. “Please remove RepViz-manual.pdf in top level directory by `git -rm`”
- 8. “please remove the the build/ directory from git; this is generated during the R CMD build process.”
- 9. “Please make sure that the maintainer of the package is registered at the Bioconductor support site”
- 9. “Add package to watch tags on support site as indicated by BiocCheck”
- 10. “Please ensure that your [webhook](https://github.com/Bioconductor/Contributions/blob/master/CONTRIBUTING.md#adding-a-web-hook) is set up”
- 10. “Submit your changes to Bioconductor to get build reports on all operating systems.”
- 11. “The organization of the repo could use some work.”
- 11. “please make sure that the master branch contains only material related to the package, e.g., the GSE107991 is not part of the package.”
- 12. “Don't hesitate to ask on the bioc-devel mailing list if you need advice about this.”
- 13. “you **really** need to spend some time familiarizing yourself with the basic concepts of Bioconductor release and development cycles”
- 13. “Please take a read of https://contributions.bioconductor.org/ to ensure that your package complies with this advice.”
- 14. “We are looking into the Windows issue you have encountered, it is most likely identified already. Please try again.”
- 14. “please do a version bump to trigger a new build and ensure all ERROR/Warnings/Notes are addressed.”
- 15. “please follow the instructions for [submitting related packages][]”
- 15. “This package should be officially submitted to Bioconductor for review as stated when the package data was originally submitted”
- 16. “So you and I both use BioC 3.10 to develop, test, and review the package.”
- 17. “We recommend packages only get submitted to CRAN or Bioconductor and not both but you have the badges for both.”
- 17. “Please don't jump the gun and advertise the package as installable from Bioconductor.”
- 18. “Please comment on your ability to address these concerns by the deadline.”
- 18. “Or if you think this will take elongated time, also let us know, so that we can close this issue temporarily, and reopen it whenever you feel ready.”
- 19. “please have each author confirm, via posting a comment in this issue or emailing me (Martin.Morgan at RoswellPark.org) directly, that inclusion in Bioconductor is acceptable.”
- 19. “are you able to provide maintenance, assistance and bug fixes for this package long term?”
- 20. “your repo has only 1 commit with everything. This is not a good practice in general”
- 21. “I am wondering if you had any AI assistance. If so we require a disclosure in this issue.”
- 22. “We would prefer that this contribution were simply an update to [HTSanalyzeR][].”
- 22. “Does your package really have to be named RIVERpkg? It seems like it would be better to omit the "pkg" part of the name and leave it at RIVER.”

## build_check

_R CMD build/check errors, warnings, notes, timings, platforms_

| # | Item | reviews | first | new | legacy |
|---|---|---|---|---|---|
| 1 | Run R CMD build and R CMD check (plus BiocCheck) locally on the final package, and fix all errors and warnings. Fix or justify every NOTE before submitting or requesting re-review. | 67 | 3% | 4% | 3% |
| 2 | Resolve 'no visible binding for global variable' and 'no visible global function definition' notes. Use utils::globalVariables(), importFrom declarations (e.g. stats, methods), qualified calls, or refactor non-standard evaluation (dplyr/aes) instead of ignoring them. | 60 | 3% | 1% | 3% |
| 3 | Check the Bioconductor build report (devel/nightly and single package builder) after each push. Confirm the package builds and installs on all platforms, and fix every error, warning and note shown. Bump the version if needed to trigger a new build, and allow for the next devel build before expecting the package to be available. | 45 | 2% | 2% | 2% |
| 4 | Remove generated, hidden and non-standard files from the package: inst/doc, doc/, build/, compiled .o/.so files, .Rproj, .DS_Store, .Rhistory, Rplots.pdf, .git, vignette HTML/PDF outputs, build scripts and top-level extras. Add development-only files (.github, data-raw, dev, pkgdown) to .Rbuildignore. | 40 | 2% | 2% | 2% |
| 5 | Make the vignette build under R CMD build in the standard build system, without --no-build-vignettes. Fix vignette errors and warnings, declare the vignette engine and suggested packages (e.g. knitr, markdown), and avoid failures from missing packages, external services or Python setups. | 28 | 1% | 1% | 1% |
| 6 | Investigate and fix specific runtime errors and failures reported in the build report (e.g. object not found, depth errors, case-mismatched filenames, failures on a particular builder). Reproduce locally and explain any environment-specific failures. | 24 | 1% | 1% | 1% |
| 7 | Make all examples and unit tests run without errors or warnings under R CMD check, on all platforms (Linux, macOS, Windows). Fail gracefully when remote resources are unavailable, and do not open browsers or UI windows. | 23 | 1% | 0% | 1% |
| 8 | Reduce the source tarball to under the Bioconductor 5 MB limit and shrink installed sub-directories (doc, extdata, libs) below the 1 MB check thresholds. Compress or resave data, shrink vignette images, and purge large files from git history. | 23 | 1% | 1% | 1% |
| 9 | Clean up compiled code: register native routines and disable dynamic symbol lookup. Remove calls to printf, puts, exit, abort, std::cout and std::cerr. Fix compiler warnings, protect R objects (rchk), and handle user interrupts. | 18 | 1% | 1% | 1% |
| 10 | Keep R CMD check runtime under 10 minutes (build time also under 10 minutes), within the memory guideline. Use minimal example data, reduce slow vignette chunks and example downloads, and keep the vignette build working on low-RAM machines. | 16 | 1% | 1% | 1% |
| 11 | Make src/Makevars and Makefile portable and located correctly within the package. Avoid GNU make extensions and non-portable flags (-O3, -march=native), and use matching OpenMP flags and a valid C++ standard. Handle missing omp.h on macOS, and provide configure.ac alongside any generated configure. | 16 | 1% | 0% | 1% |
| 12 | Resolve Windows support issues: fix Windows compilation, load and path-length problems, or explain what fails and mark the package unsupported with a .BBSoptions file. Ensure native or conda-based dependencies install from source. | 14 | 0% | 0% | 0% |
| 13 | Fix DESCRIPTION and NAMESPACE dependency notes: declare used packages (e.g. methods, markdown) in Imports, Depends or Suggests, remove unused imports, and resolve 'Depends not imported from' and missing import errors. Declare the R version dependency when serialized objects require it. | 13 | 0% | 0% | 1% |
| 14 | Fix warnings emitted at install or load time (multiple methods tables, reticulate virtualenv, annotation package loading, 'added imports' messages) and ones raised by vignette or example code, such as replacement-length and deparse cutoff warnings. | 12 | 1% | 3% | 0% |
| 15 | Develop and test against current R-devel and Bioconductor devel (with up-to-date packages), and report sessionInfo(). Confirm the package also builds on R-release. | 11 | 0% | 0% | 0% |
| 16 | Fix documentation problems flagged by check: Rd line width, lost braces, empty Rd sections, usage/code mismatches, unresolved file links, and example parse errors. Wrap long example lines and regenerate docs with current roxygen. | 11 | 0% | 0% | 1% |
| 17 | Fix argument and S3 consistency problems flagged by check: partial argument matching, S3 method signatures that must match their generics (print, summary, predict), and generic/method consistency warnings. | 7 | 0% | 0% | 0% |
| 18 | Fix package metadata files: put the citation in inst/CITATION in valid format, make NEWS parseable by utils::news(), use a 0.99.z version for new packages, and keep a single README. | 7 | 0% | 0% | 0% |
| – | _unmatched points_ | 3 | | | |

Typical wording:

- 1. “Fix or otherwise address all WARNINGs raised by `R CMD check` and `BiocCheck::BiocCheck()`”
- 1. “`R CMD build` without errors, warnings, notes (verify locally).”
- 2. “Recommend cleaning up the global variable and function NOTES”
- 2. “Undefined global functions or variables:”
- 3. “[REQUIRED] Make sure your build report is clean. Address all the NOTEs before a further review.”
- 3. “Please clean up as many NOTES as possible from the build report”
- 4. “Some of the files exceeding the limit are `inst/doc/scLANE.html` and `src/scLANE.so`.”
- 4. “Remove `.RData` and `.Rhistory` files from the package directory. These files cannot be part of the package, and should be added to `.gitignore`”
- 5. “The python pipeline should be runnable during package build.”
- 5. “Error: processing vignette 'MotifPeeker.Rmd' failed with diagnostics:”
- 6. “I get the same errorfrom above when performing `plotDataHeatmap()` on the df from factor2 (line 268).”
- 6. “When ChemmineOB is installed the package fails to check locally for me”
- 7. “❯ checking examples ...sh: line 1: 8942 Abort trap: 6”
- 7. “Error in readFCSgetPar(x, paste("$P", 1:nrpar, "B", sep = "")) : Parameter(s) $P1B not contained in 'x'”
- 8. “NOTE: checking installed package size. Installed size is 8.2Mb, data directory is 6.6Mb.”
- 8. “* checking installed package size ... NOTE”
- 9. “Compiled code should not call entry points which might terminate R nor write to stdout/stderr instead of to the console, nor use Fortran I/O nor system RNGs.”
- 9. “rchk suggests you might need to `PROTECT()` before calling `set_pkgname_attr()`”
- 10. “The whole check process requires less than 5 mins.”
- 10. “`R CMD check --no-build-vignettes` within 10 minutes.”
- 11. “It will be better to provide documentation to resolve this issue.”
- 11. “The `R CMD INSTALL` output shows several errors and warnings (`clang: error: no input files`, `awk: syntax error`, `clang: warning: unused variable`)”
- 12. “I think it's easy to set a `.BBSoptions` file in your package.”
- 12. “Is this package not meant to be run on windows?”
- 13. “Namespace in Imports field not imported from: ‘svglite’ All declared Imports should be used.”
- 13. “ERROR: Packages (HiveR) which provide adj2HPD (used in NA) should be imported in the NAMESPACE file, otherwise packages that import MoonlightR could fail.”
- 14. “Warning: multiple methods tables found for 'group'”
- 14. “Note: wrong number of arguments to '=='”
- 15. “You should be testing on the devel branch of R.”
- 15. “Please check these following `WARNINGS` as well. (use R-devel)”
- 16. “Variables with usage in Rd file 'example_dataset.Rd' but not in code:”
- 16. “\examples lines wider than 100 characters”
- 17. “checking S3 generic/method consistency ... WARNING predict: function(object, ...) predict.grridge:”
- 17. “You have defined methods for the S3 generics print() and summary(), but the method signatures don't match the generic ones.”
- 18. “Fix Citation location NOTE. remove the .md extension.”
- 18. “Make sure it’s parseable by `utils::news()`”

## performance

_speed, memory, parallelisation (BiocParallel)_

| # | Item | reviews | first | new | legacy |
|---|---|---|---|---|---|
| 1 | Use BiocParallel (e.g. bplapply) for all parallelisation instead of parallel, mclapply, makeCluster, foreach/doParallel/doSNOW, Rmpi or custom backends, or justify why not. Do not branch on OS or on MPI availability. | 76 | 5% | 6% | 5% |
| 2 | Vectorise for-loops and nested sapply/lapply iterations (element-wise assignment, matrix index assignment, rnorm/rnbinom draws, column normalisation, string operations, pairwise comparisons) following the Bioconductor efficient-code guidelines. Avoid per-row data.frame operations. | 43 | 3% | 3% | 3% |
| 3 | Replace apply() over matrix rows or columns with optimised functions: rowSums/colSums/rowMeans/colMeans, or matrixStats equivalents (rowMins, rowMaxs, colMedians, rowVars, colSds, colWeightedMeans). Use rowsum or tapply for grouped sums and means. | 41 | 2% | 1% | 3% |
| 4 | Expose a `bpparam` argument on every parallelised function, defaulting to `BiocParallel::bpparam()` or `SerialParam()` (not NULL). Accept any BiocParallelParam and pass it straight to bplapply. Replace cores/ncores/cpus/numThreads/parallel arguments with it. | 30 | 1% | 3% | 1% |
| 5 | Pre-allocate result vectors, lists and matrices instead of growing them by copy-and-append (c(), rbind/cbind in loops, repeated merge). Alternatively use lapply/vapply followed by unlist or a single do.call(rbind, ...). | 29 | 2% | 1% | 2% |
| 6 | Hoist loop-invariant computations, function definitions, accessor calls (e.g. assay(), otu_table()), conditionals and repeated identical expressions out of loops and apply calls. Compute shared values once. | 22 | 1% | 0% | 2% |
| 7 | Reduce memory use. Avoid densifying sparse or delayed input (as.matrix), and support DelayedArray/HDF5/on-disk or lazy representations for large data. Document memory limits, build sparse objects directly, and remove explicit gc()/rm() calls. | 21 | 1% | 2% | 1% |
| 8 | Do not choose the number of cores for the user. Do not call detectCores(), register backends inside functions, or create the BiocParallel param internally. Default to 1 or 2 workers and let users control parallelism via `register()` or the argument. Limit workers to 1-2 in examples and vignettes. | 19 | 1% | 0% | 1% |
| 9 | Minimise web and API overhead. Batch queries (KEGG, biomaRt, etc.) instead of one request per item, cache downloads with BiocFileCache, and handle rate limits with retries and timeouts. Add progress reporting for slow steps, and prefer local data over online lookups. | 16 | 1% | 3% | 1% |
| 10 | Profile and speed up functions that are reported as slow or that scale poorly (quadratic cost). Report timings on realistic data and, where claimed, demonstrate performance against comparable packages. | 15 | 1% | 1% | 1% |
| 11 | Shorten example, vignette and R CMD check run time (target under ~5-10 minutes) by using smaller datasets, fewer iterations or subsets. Remove unnecessary Sys.sleep calls, and justify any code that cannot run in examples or vignettes. | 14 | 1% | 1% | 1% |
| 12 | Remove unnecessary manual optimisations and calls: explicit cmpfun, gc() and rm(), and wrappers around BiocParallel (e.g. get_bpparam). Use simpler built-ins instead (startsWith, any(), crossprod, order(decreasing=TRUE)). | 13 | 1% | 1% | 1% |
| 13 | Make parallel code portable and safe. Remove OS-specific calls (e.g. renice, manual OS checks, Windows bypasses), avoid nested parallelism (parallelise the outermost loop only), and make sure worker functions work under SnowParam by loading required namespaces. Do not overwrite or ignore bpexportglobals settings. | 12 | 0% | 0% | 0% |
| 14 | Avoid repeated expensive calls and scans: use grouping, split, findInterval, or lookup tables instead of repeated which()/findOverlaps/match calls. Merge multiple quantile or apply calls into one with vector arguments. Memoise recursive functions. | 11 | 1% | 1% | 1% |
| 15 | Reduce source and installed package size (target under 5 MB). Compress saved data, trim extdata and images, drop unneeded genome packages, and purge large files from git history. | 10 | 1% | 0% | 1% |
| 16 | Check whether vectorisation makes parallel evaluation unnecessary, and justify any parallelism that remains. | 4 | 0% | 0% | 0% |
| 17 | Avoid copying large objects on each element update (matrix, nested S4 objects). Update them once outside the loop, or use initialize() to set all slots at once. | 4 | 0% | 0% | 0% |
| 18 | Minimise file I/O and serialisation overhead. Return vectors and write once, delete temporary files once consumed, and reuse objects already created instead of reloading files. | 4 | 0% | 1% | 0% |
| – | _unmatched points_ | 8 | | | |

Typical wording:

- 1. “We prefer for you to make use of `BiocParallel`, that supports a selection of parallelisation backends, and thus greater flexibility for the users.”
- 1. “Use `BiocParallel::bplapply()` rather than `mclapply()` for portability; make sure your code works with `register(SnowParam())`”
- 2. “There are many matrix operations which can be optimized in TADBD.R. You use too many nested forloops.”
- 2. “There are potential performance improvements possible for `checkInclusion` e.g., by using all the combinations of comparisons (with `combn`) across all elements and identifying subsets that way.”
- 3. “you can replace the `apply()` call with setDF <- replace_na(colMeans(setDF) * 100, 0)”
- 3. “Use the package "matrixStats" to calculate `rowMeans`, `rowMedians` etc. These are highly optimized functions”
- 4. “Please either explicitly document this, or (as many packages do), expose an `BPPARAM` argument”
- 4. “the top-level function should have a `BPPARAM` argument that accepts a user-supplied _BiocParallelParam_ instance (with a default value of `BiocParallel::SerialParam()`).”
- 5. “it is usually very inefficient to 'copy and append'; instead use 'pre-allocate and fill' or (often even better) R's `lapply()`”
- 5. “Some `do.call(cbind, ...)` calls might be replaced by the more performant `list2DF()` base function.”
- 6. “Consider 'hoisting' the constant conditional outside the function definition (similarly for `g()`).”
- 6. “There seems to be a lot of code which is running in the loops, and doesn't need to be inside the loop.”
- 7. “Consider supporting a sparse format (like `MatrixMarket`; MTX) in the Java backend, or at minimum, add a strong warning or size check before coercing large sparse matrices.”
- 7. “It is almost never necessary to call `rm()` and `gc()`. If memory is a problem, it is best to iterate.”
- 8. “I believe `.generateBPParam()` is not as straightforward as what you currently have. There are other context where forking doesn’t work well. In RStudio for example.”
- 8. “I found the instructions about selecting the number of cores confusing, could this be handled automically in the code?”
- 9. “Look over our notes for querying web resources (http://bioconductor.org/developers/how-to/web-query/). You may find helpful information to be sure your package doesn't TIMEOUT”
- 9. “The KEGG query ... is one gene at a time. The API supports multiple queries, using `+` as a separator, and this will be much more efficient.”
- 10. “The user needs to remember to set the `deterministic` argument to `FALSE` to actually fully benefit from multithreading.”
- 10. “some demonstration that the performance of **fenr** is superior to other packages”
- 11. “you may need to switch the examples in the vignette and documentation to smaller (or subsetted) genomes”
- 11. “address overall compute time by reducing the example size or vignette extent, or by identifying and addressing inefficient R code.”
- 12. “`any()` would be clearer and give you better performance on booleans”
- 12. “no need to call `cmpfun` explicitly; functions are compiled when the package is installed.”
- 13. “it is seldom necessary to mix parallel processing (mclapply / foreach) paradigms; stick with one”
- 13. “BiocParallel will create the appropriate BPPARAM for any OS - so if on windows the workers are socket clusters, if on linux/mac they are forks.”
- 14. “A final improvement likely to be relevant in real cases is to 'memoise' the `get_num_paths()` function.”
- 14. “you might as well use a single `apply()` with a vector as the `probs` argument call instead of multiple `apply()` calls.”
- 15. “Installation takes a very long time because BSgenome.Hsapiens.UCSC.hg38_1.4.5.tar.gz, BSgenome.Hsapiens.UCSC.hg18_1.3.1000.tar.gz and BSgenome.Hsapiens.UCSC.hg19_1.4.3.tar.gz are installed.”
- 15. “Installed package size is 8.8Mb, please work on decreasing the size.”
- 16. “Is parallel evaluation necessary here? it seems like this could be written in a vectorized manner?”
- 16. “Maybe with vectorization it will NOT be necessary to use parallel evalation?”
- 17. “Consider instead using `initialize()` to update all slots in one call.”
- 18. “this I/O overhead might dominate the actual KNN compute time for smaller datasets.”
- 18. “minimize the number of times data is written to a file by returning vectors from calculations, and writing the vector.”

## fit_overlap

_fit for Bioconductor, overlap with existing packages, scope, interoperability_

| # | Item | reviews | first | new | legacy |
|---|---|---|---|---|---|
| 1 | Explain in the vignette introduction and DESCRIPTION how the package differs from existing Bioconductor and CRAN packages of similar scope, and name those packages concretely. Include a comparison table where useful, and justify any new implementation of functionality that already exists. | 60 | 4% | 7% | 3% |
| 2 | Split the package if it mixes distinct audiences or concerns, such as analysis, plotting, Shiny apps, infrastructure, data, utilities or reporting. Move Shiny apps and large plotting or analysis code into separate packages so each package has a clear focus, and decide which functions belong where. | 37 | 2% | 3% | 2% |
| 3 | Use standard Bioconductor data structures (SummarizedExperiment, SingleCellExperiment, SpatialExperiment, MultiAssayExperiment, GRanges/GRangesList, Biostrings classes, TreeSummarizedExperiment, and so on) for inputs and outputs. Do not use custom S3 classes or data.table as the main representation. Accept data.frame or matrix input where appropriate, coercing inside the function. | 28 | 1% | 1% | 2% |
| 4 | Do not reimplement algorithms or statistical methods that already exist in established packages. Examples are findOverlaps, scuttle/scrapper PCA and UMAP, limma, msqrob2, cleaver, GSEA/ORA methods, stats functions such as uniroot and ecdf, and DropletUtils. Call the existing implementation, contribute upstream, or state clearly what is novel. | 26 | 2% | 3% | 2% |
| 5 | Reuse existing Bioconductor file import and export functions instead of writing custom parsers or writers. Examples are rtracklayer import/export for BED, GFF, GTF and bigWig, VariantAnnotation for VCF, the GSEABase and Biostrings readers, and the MsBackend export backends. Any helper that is retained should be a thin wrapper or return compatible output. | 25 | 1% | 2% | 1% |
| 6 | Justify why the package belongs in Bioconductor rather than CRAN. Show a real dependency on and integration with Bioconductor infrastructure, and state the added value beyond thin wrappers of existing tools. If integration is out of scope, consider submitting to CRAN. | 20 | 1% | 0% | 1% |
| 7 | Demonstrate interoperability with related Bioconductor packages and workflows. Show in the vignette how outputs of other packages feed into this one and vice versa, and avoid decomposing standard objects or building a standalone pipeline. | 20 | 1% | 2% | 1% |
| 8 | Reuse existing Bioconductor annotation and data resources (TxDb, ensembldb, org.*, BSgenome, AnnotationHub, msigdb, biomaRt, GenomicDataCommons) instead of bundling or precomputing duplicate annotation data or custom downloaders. Clarify any overlap with these resources, and justify any separate data or experiment-data package. | 20 | 1% | 1% | 1% |
| 9 | Define the package scope clearly and state it consistently in the title, DESCRIPTION and vignette. Cover the supported data modalities, file types and formats, and versions. Make sure the package offers enough substantive functionality to justify inclusion. | 18 | 1% | 0% | 1% |
| 10 | Provide convenient helpers for getting data into the package's format, such as converters from common objects or formats and functions to browse or list available resources. Document any required file layouts, prefer base data representations over directory-based or text-file inputs, and support multiple or vectorised inputs in a single call. | 16 | 1% | 0% | 1% |
| 11 | Reduce the exported API surface. Make helper and utility functions internal, and remove thin wrappers that add little value over base or existing functions. Limit the number of new generics, methods and classes, and wrap object and method operations in documented user-facing functions. | 15 | 1% | 2% | 1% |
| 12 | Keep each function focused on a single task. Separate analysis, plotting, saving and preprocessing steps into distinct functions, and provide exported plotting functions rather than flags such as doplot. Consolidate near-duplicate functions into general ones (for example per-dimension, per-disease or per-input-type variants). | 14 | 1% | 1% | 1% |
| 13 | Return objects (data.frames, plot objects, results) from functions instead of writing files by default. Make any file output optional, with an explicit output path or directory argument, so nothing is written to the user's working directory and functions run interactively. | 11 | 1% | 0% | 1% |
| 14 | Avoid hard-coded assumptions about user data. Expose arguments for column names (logFC, p-value, study and cell-type variables), thresholds, naming schemes and supported alphabets. Accept results from alternative upstream tools (edgeR, DESeq2, limma) rather than only one, and detect input origin programmatically, failing with a clear message. | 11 | 1% | 0% | 1% |
| 15 | Generalise beyond a single organism or genome build (human/mouse only, hg19/hg38 only) by exposing TxDb, org or assembly parameters, or else document and justify the restriction. Support other species and reference sources where reasonable. | 9 | 1% | 3% | 0% |
| 16 | Avoid masking or conflicting with functions, classes or S3/S4 methods in other packages (for example biclust::discretize or tidySummarizedExperiment verbs). Reuse existing generics such as plot. The package must not break other packages on the search path and must not rely on load-time warnings or conflicted. | 6 | 0% | 0% | 0% |
| 17 | Choose clear, descriptive names for the package, functions and classes. They should not imply unintended comparisons, be too similar to existing software, be vague, or reflect usage instead of what the object is. | 6 | 0% | 0% | 0% |
| 18 | Ensure the vignette demonstrates the claimed use cases and relevance to the broad Bioconductor audience. Add functions that generate the plots shown, and remove claims or biocViews that are not supported. | 5 | 0% | 2% | 0% |
| 19 | Check documentation and compliance for platform and source constraints. Make any bundled non-R source code (Java, C++) publicly available in a versioned repository and justify its use over existing libraries such as htslib. Mark unsupported platforms explicitly. | 4 | 0% | 0% | 0% |
| 20 | Follow Bioconductor conventions for coordinates and overlap semantics (1-based closed intervals). If a function mimics an existing one such as findOverlaps, match its arguments and behaviour or document the differences, including support for GRangesList, empty ranges and circular sequences. | 2 | 0% | 0% | 0% |
| – | _unmatched points_ | 4 | | | |

Typical wording:

- 1. “It seems like functionality such as ORA is already available in Bioconductor. Have you looked at the `EnrichmentBrowser`?”
- 1. “Please also provide a comparison to existing Bioconductor packages, such as [MetaboCoreUtils]”
- 2. “consider creating a utility package with exported helpers for users looking to use the same operations.”
- 2. “Could you consider merging some of the packages? Can you imagine cases where users may have interest in using just one of them”
- 3. “I don't see any interoperability with standard Bioconductor data structures. Please update, including in response to the following comments.”
- 3. “Please support `SummarizedExperiment` input and classes related to proteomics.”
- 4. “Avoid repeating functionality already present in Bioconductor, e.g., PlotVolcano_*, PlotOmics*, etc.”
- 4. “could the hypergeometric testing be carried out in the context of an existing ORA package?”
- 5. “Since this has the potential to be a newly recommended way of importing a different file type I am asking @hpages and @mtmorgan”
- 5. “There is a `readBed` function but Biocoductor already has a function in [rtracklayer]”
- 6. “If the package does not pivot to leverage established Bioconductor infrastructure, it is better suited for a CRAN submission.”
- 6. “I don't see why you chose Bioconductor for this package. How does it interoperate with other packages?”
- 7. “for sufficient interoperability you would at least want to depend on a package like `EBImage`”
- 7. “There seems to be very little interconnection with existing Bioconductor packages and structure.”
- 8. “It's a bad idea to include your own annotations in the package (e.g. the `hg19`, `hg38`, and `mm10` data sets).”
- 8. “There's a lot of unnecessary work here mapping genome symbols to `org.*`”
- 9. “'Pipeline' packages are seldom successful, because they necessarily make too many assumptions about the user data and stability of dependent packages.”
- 9. “Is the package's main aim to provide an API to the data? There are examples of analyses and plotting which may be more appropriate in another package(s).”
- 10. “The `getNCBIGene2KEGG()` function is not vectorized so the user who needs to map a set of genes will need to apply `getNCBIGene2KEGG()` in a loop.”
- 10. “Do your functions always need to fully complex list of lists objects or can individual data.frames be provided at each step?”
- 11. “Functions such as `load_sqlite` more often than not belong in the software package as unexported utility functions”
- 11. “Is this function necessary? You have saved datasets as examples and presumably others will have their own data to analyze.”
- 12. “the user only need to specifiy the object, then a selection of defaults could be used to do the calculation.”
- 12. “Instead of creating a new function for every disease/tissue I would recommend a single download or extract function”
- 13. “these functions create the file to display the plot... It would be better to instead simply return the plot from these functions and allow the user to save it to a file themselves.”
- 13. “It would be better to let users save their own `.Rda` files rather than providing a function like `save_new_model`”
- 14. “your functions could take an `alphabet` argument with default value `c("A", "T", "C", "G")`.”
- 14. “There is no need to have the function do this directly and return a (duplicated) subset of the data that is tied to a specific FDR.”
- 15. “Please clarify why **EpiCompare** is restricted to just hg19 or hg38.”
- 15. “Consider to expose the Annotation TxDb or Org package as parameters to handle species other than human hg19 only.”
- 16. “Why have you not implemented all of filter(), select(), summarize(), mutate() and arrange()? Why are you using data.table instead of tbl?”
- 16. “Wherever possible, please use an existing generic such as `plot` for creating plots.”
- 17. “Calling it __betterChromVAR__ implies that chromVAR is somewhat worse.”
- 17. “Consider renaming `CreateTomo` to something like `checkTomo` as 'Tomo' is not really a class”
- 18. “How will it be useful to anyone not studying carcinoma? Please justify why this package should be part of Bioconductor and useful to many users, not only a niche audience.”
- 18. “I would expect to see some regions of interests or masks overlaid on my input image”
- 19. “Also I wonder where **ompBAM** stands with respect to HTSlib. Is **ompBAM** exposing a C++ API for accessing BAM files?”
- 19. “The java source code needs to be available, preferably in a versioned (e.g., github) repository.”
- 20. “So ideally these differences would need to be addressed, or, at the very least, they would need to be clearly documented.”
- 20. “it looks like you have adopted a '0-based, half-open' coordinate system, where Bioconductor uses '1-based, closed' coordinates.”

## BiocCheck

_BiocCheck notes/warnings/errors as such_

| # | Item | reviews | first | new | legacy |
|---|---|---|---|---|---|
| 1 | Run BiocCheck::BiocCheck() (and BiocCheckGitClone() on the repository) after every update, then fix all reported errors and warnings and as many notes as possible. Justify any note you leave unfixed. | 91 | 5% | 7% | 5% |
| 2 | Go through the build report (R CMD check and BiocCheck output) line by line and resolve every error, warning and note, including typos and other minor items. | 41 | 2% | 0% | 3% |
| 3 | Resolve 'no visible binding' and 'no visible global function definition' notes by importing the needed functions (importFrom, including from methods), using .data, qualifying calls with pkg::, or declaring variables with utils::globalVariables(). | 18 | 1% | 0% | 1% |
| 4 | Fix DESCRIPTION issues: set Depends R to the required version, remove LazyData or set it to false, add a valid ORCID for the maintainer and a fnd role if applicable, and make sure URL and BugReports fields are present. | 13 | 1% | 0% | 1% |
| 5 | Clarify how objects flagged as undefined or uninitialized are created, for example via data(), with() or within(), so the checker can see their definition. Rewrite the code where necessary. | 12 | 1% | 0% | 1% |
| 6 | Remove redundant 'error', 'stop' or 'warning' wording from condition messages, and drop duplicate stop/warning calls inside handlers, to clear the redundant-signal note. | 10 | 0% | 1% | 0% |
| 7 | Complete the man pages: add a non-empty \value or @return section to every Rd file, add runnable examples to documented functions, document all exported objects and functions, and use \donttest instead of \dontrun. | 10 | 1% | 2% | 0% |
| 8 | Do not use paste() or paste0() inside stop(), warning() or message(). Pass the pieces as separate comma-separated arguments. | 8 | 0% | 0% | 0% |
| 9 | Use '<-' instead of '=' for assignment. Avoid '<<-' by returning values instead. Use TRUE/FALSE rather than T/F. | 8 | 0% | 1% | 0% |
| 10 | Wrap R code, vignette and example lines to 80 characters or fewer, and indent in multiples of 4 spaces. | 8 | 1% | 0% | 1% |
| 11 | Shorten functions longer than 50 lines by splitting them into helpers. | 8 | 0% | 0% | 1% |
| 12 | Replace 1:n and 1:length(x) with seq_len() or seq_along(), and replace sapply() with vapply() or another type-safe alternative. | 7 | 0% | 0% | 0% |
| 13 | Replace class() equality checks with is(), use accessor methods instead of '@' slot access in code and examples, and fix deprecated usage such as .Deprecated and '.names' replacement. | 7 | 0% | 3% | 0% |
| 14 | Add a NEWS file with an entry for each version, and add Bioconductor installation instructions using BiocManager to the README. | 6 | 0% | 1% | 0% |
| 15 | Reduce package and repository size below the Bioconductor limit by cleaning git history and shrinking data. Remove unnecessary, hidden, system and compiled object files from the repository. | 6 | 0% | 1% | 0% |
| 16 | Remove cat() and print() calls used for output outside show methods. Use message() or a proper show() method for each S4 class, and remove debugging output. | 5 | 0% | 3% | 0% |
| 17 | Remove set.seed() calls from package functions and expose a seed argument only where needed. Avoid suppressWarnings() and suppressMessages() around whole blocks, and use them only on specific calls with an explanation. | 5 | 0% | 3% | 0% |
| 18 | Make sure packages used in code are declared correctly: list vignette and example dependencies in Suggests, import or remove packages named in DESCRIPTION but missing from NAMESPACE, and avoid library() and require() calls in package code and vignettes. | 4 | 0% | 0% | 0% |
| 19 | Subscribe the maintainer to the bioc-devel mailing list and register on the Bioconductor support site. | 4 | 0% | 0% | 0% |
| 20 | Remove non-ASCII characters from code, data and documentation, and make the CITATION file readable by readCitationFile(). | 3 | 0% | 0% | 0% |
| 21 | Add the biocViews terms that BiocCheck suggests, such as clustering or KEGG. | 3 | 0% | 0% | 0% |
| 22 | Use evaluated vignette code chunks with correct chunk syntax, and remove install calls from vignette code. | 3 | 0% | 0% | 0% |
| 23 | Use BiocFileCache for downloaded files instead of calling download.file() directly, and do not override getOption('repos') with non-Bioconductor repositories. | 2 | 0% | 1% | 0% |
| – | _unmatched points_ | 13 | | | |

Typical wording:

- 1. “There are some NOTES from `BiocCheck::BiocCheck()`, please address as many of thes as possible”
- 1. “Some of the notes issued by `BiocCheck()` (see link to build report above) need your attention e.g. "Avoid using '=' for assignment and use '<-' instead"”
- 2. “Ther are some `BiocCheck` notes in the build report, please check these and address them if necessary”
- 2. “Please see the build report NOTE instances; all of these should be tried to be addressed.”
- 3. “Please do not ignore these 2 `R CMD check` NOTEs:”
- 3. “getOutput: no visible binding for global variable 'workflowName'”
- 4. “`BiocCheck` notes that there is no `"fnd"` role under `Authors@R`;”
- 4. “NOTE: 'LazyData:' in the 'DESCRIPTION' should be set to false or removed”
- 5. “NOTE: Consider clarifying how 4 object(s) are initialized. Maybe they are part of a data set loaded with data(), or perhaps part of an object referenced in with() or within().”
- 5. “Consider clarifying how 2 object(s) are initialized. Maybe they are part of a data set loaded with data(), or perhaps part of an object referenced in with() or within().”
- 6. “change or remove the word `warning`, or `error` to other word”
- 6. “NOTE: Avoid redundant 'stop' and 'warn*' in signal conditions”
- 7. “please address the warning raised by BiocCheck (`WARNING: Empty or missing \value sections found in man page(s).”
- 7. “Undocumented code objects: ‘generateBPParam’”
- 8. “NOTE: Avoid the use of 'paste' in condition signals”
- 8. “Avoid `paste` inside condition signals (e.g., `message(1, "abc", 2)` works without pasting)”
- 9. “* NOTE: Avoid using '=' for assignment and use '<-' instead”
- 9. “See comment above from @mtmorgan about global environment. This should be corrected.”
- 10. “Consider multiples of 4 spaces for line indents, 1029 lines(36%) are not.”
- 10. “in the `BiocCheck()` report, there are NOTEs related to the number of characters in examples (> 100 characters make things hard to read”
- 11. “Please address as many of the remaining BiocCheck notes as possible:”
- 11. “The recommended function length is 50 lines or less. There are 51 functions greater than 50 lines.”
- 12. “Please clean up coding notes about Avoiding 1:...”
- 12. “Check the `BiocCheck` results and follow the recommendations for avoiding `sapply` etc.”
- 13. “Please see coding practice Warning about using `is()` rather than `==/!=`”
- 13. “`BiocCheck` notes that `@` usage is being detected.”
- 14. “- [ ] Include Bioconductor installation ``` source("http://bioconductor.org/biocLite.R") biocLite("MICMIC")”
- 14. “Include instructions on how to install from Bioconductor in your `README`.”
- 15. “Package Source tarball exceeds Bioconductor size requirement, package size is 5.2MB and our size requirement is 5.0MB.”
- 15. “Warning: inst/doc file GGPA-example.pdf ignored as vignettes have been rebuilt.”
- 16. “NOTE: Avoid 'cat' and 'print' outside of 'show' methods”
- 16. “There are various `BiocCheck` notes regarding messages/warnings, `cat/print()`, etc.; please try to address them”
- 17. “This is the only BiocCheck WARNING and submission requires none.”
- 17. “Package code should not set the seed, this is left to the user.”
- 18. “Packages used only in man page examples and/or the vignette need to be in the Suggests field.”
- 18. “There is WARNING in the build report about library/require call”
- 19. “ERROR: Maintainer should subscribe to the bioc-devel mailing list.”
- 19. “Please register with the Bioc support site at https://support.bioconductor.org/”
- 20. “checking data for non-ASCII characters ... NOTE”
- 20. “Citation file (if present) in correct format (`readCitationFile("inst/CITATION")` without error).”
- 21. “NOTE: Consider adding these automatically suggested biocViews: Clustering”
- 21. “consider adding these automatically suggested biocView: Alignment, SequenceMatching.”
- 22. “The following warning can be avoided by using single `` ` `` instead of `` ``` `` to highlight variables in the vignette:”
- 22. “WARNING: Evaluate more vignette chunks. 10 out of 13 code chunks = 76% unevaluated”
- 23. “Files downloaded should be cached. Please use BiocFileCache”
- 23. “'getOption("repos")' replaces Bioconductor standard repositories, see 'help("repositories", package = "BiocManager")'”
