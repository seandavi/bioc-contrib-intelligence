# Example reviews

Representative first full reviews and follow-ups, verbatim except that GitHub logins are replaced with role labels (reviewer-n, submitter-n, user-n). Package names are kept. Picked by reading candidates that cover many checklist categories, from different reviewers; see `LEDGER.md`.

## LIPIDIFy: first full review (new tracker, 2026-07)

_New tracker; checkbox list grouped by file, 13 categories, one follow-up._

````markdown
Hi @user-1  Thank you for submitting your package to Bioconductor! Please consider addressing the following comments:

# Package structure 

- [ ] remove `.Rproj` file and all `.DS_Store` files
- [ ] please fix any errors/warnings in `BiocCheck()`

## README

- [ ] include Bioconductor installation instructions in README file
- [ ] remove the empty `README.md` in the vignettes folder

## DESCRIPTION

- [ ] remove `devtools` from `Suggests`
- [ ] consider adding "Software" and the automatically suggested term "Classification" to `biocViews`

## NAMESPACE

- [ ] the package mixes explicit namespace calls (`pkg::fun`) and `importFrom()`. Consider using one approach consistently throughout the package to make the code and dependency management easier to follow
- [ ] add package-level man page

## extdata

- [ ] the file `demo_lipidomics.R` in `inst/extdata` is not used anywhere in the package. Is it a real data example? If so, i recommend using it in the vignette instead of the simulated data. For this, add the MetaboAnalyst file used in the demo to the `extdata` folder instead of exposing your path. Also, add the source of that data (where did you get it originally, e.g. link to a database). Move `demo_lipidomics.R` to `inst/scripts`
- [ ] remove commands such as `devtools::load_all(your/path)`
- [ ] could you explain where do you need the file `lipidmaps_snapshots.rds`? it doesn't appear to be used anywhere. If that's correct, please remove it

# Functionality and code

- [ ] add validity checks for all functions arguments instead of silently coercing to the desired type. e.g. a `metadata` argument is expected to be `data.frame` and contains a specific column, check whether the user passed the right format and for the existence of the specific column, and if not throw a descriptive error
- [ ] please avoid resetting the seed internally in `impute_missing_values()`, as the current implementation calls `set.seed()` without this behavior being visible to the user. If reproducibility is desired in the app, consider exposing an optional seed argument or clearly documenting how users can control reproducibility
- [ ] since `R/data.R` contains data-generation functions rather than dataset documentation, consider renaming it to something more descriptive, e.g. `generate_data.R`
- [ ] consider allowing the user to pass their own design to `perform_differential_analysis_*()` instead of having it hard coded. The shiny app could still use that default design behavior
- [ ] it is a bit difficult to differentiate between the internal functions and the exported ones. Consider adding `.` in front of internal function names, and add the tag `@user-2` to avoid generating documentation accessible by the user for those internal functions
- [ ] please remove redundant/unused functions (e.g.`run_fgsea()`). Also `normalize_lipidomics_data()` and `apply_normalizations()` (both exported) are exactly the same. Same for `example_lipidomics_data()` and `generate_example_data()`. It is confusing to the user which one to use. Consider keeping only one function
- [ ] several exported functions contain large nested helper functions that implement most of the actual logic (e.g. in `in classify_lipids()`). Consider extracting these into internal helper functions to make the code more readable and easier to maintain
- [ ] remove all commented out/old code

# Vignettes

- [ ] add in the introduction the motivation behind the package and contribution relative to existing workflows and tools for lipidomics analysis
(e.g. `lipidr` https://bioconductor.org/packages/lipidr), and emphasize the interoperability aspect within the bioconductor ecosystem. Consider the use of the Bioconductor class `SummarizedExperiment` for storing the data
- [ ] the internal documentation mentions that `edgeR` is not the recommended method for differential analysis of lipidomics data and is provided only as exploratory alternative. Please make this limitation explicit in the vignette and explain when users should select this method
- [ ] add a real example data and use it in the vignette to showcase function outputs, **most of the chunks are not evaluated**
- [ ] it is not clear right away from the vignette names what is the difference between the guide and workflow (they are more or less the same). Consider renaming the main vignette LIPIDIFy to be easily accessed using `vignette("LIPIDIFy")`
- [ ] use `BiocStyle` for vignettes formatting
- [ ] add author name in vignette `lipidomics-analyser-guide.Rmd`

# Shiny app

- [ ] when `sva` package is not installed and the user requests `ComBat` for batch correction, the app still reports that correction was performed using `ComBat`, while the fallback warning appears only in the console. Please make sure that the method displayed in the app reflects the method actually used, and return the fallback clearly to the user
- [ ] html report was empty when generated from the app (also got an error `Report failed: <text>:1:8: unexpected 'in' 1: knitr::in ^`)
- [ ] in the app, the tab naming is slightly inconsistent. e.g., enrichment results are displayed under `Enrichment Visualization`, while differential analysis under `Result Visualization`. Consider using a consistent naming scheme across tabs
- [ ] in the `Lipid Classification` tab, the table "Current Classification" is not well rendered (overflows a little bit) maybe consider making it scrollable if possible

# Tests

- [ ] please consider increasing the package coverage. 5% is very low

```
covr::package_coverage()
LIPIDIFy Coverage: 5.10%
R/shiny_app.R: 0.00%
R/visualization.R: 0.00%
R/analysis.R: 3.50%
R/utils.R: 31.75%
R/data.R: 96.70%
```
````

## LIPIDIFy: follow up (new tracker, 2026-09)

_New tracker; checkbox list grouped by file, 13 categories, one follow-up._

````markdown
@user-1 Hi Fayrouz. Thank you for addressing my comments. The package is already in a very good shape! I just have a couple of comments before I proceed with accepting it:

* please make sure you are subscribed to Bioconductor mailing list (if not subscribe here: https://stat.ethz.ch/mailman/listinfo/bioc-devel)

*  i think i wasn't very clear in one of my previous comments: could you please make sure that all functions imported in DESCRIPTION are also included in NAMESPACE. This will help with maintaining the package in the future

* please remove this sentence from the vignette : "see`data-raw/prepare_ST001359_lipidomics.R` for exactly how it was derived from the public API", since this is an internal script and is not exposed to the user

* it would be helpful for the reporoducibility of the analysis to print `sessionInfo()` at the end of the HTML report

* in the app, under the Lipid Expression tab, the lipid dropdown list for the example data includes the tumor ID and weight. i don’t think these are meant to be included there. If so, could please you fix this?

* the package coverage is currently 35.10%. please consider increasing it, ideally closer to 90% as this can help prevent the package from breaking and make it easier to maintain in the future. these links might also be helpful https://contributions.bioconductor.org/shiny.html and https://rstudio.github.io/shinytest2/

```
covr::package_coverage()
LIPIDIFy Coverage: 35.10%
R/shiny_app.R: 9.41%
R/visualization.R: 78.66%
R/utils.R: 85.28%
R/analysis.R: 86.77%
R/generate_data.R: 96.74%
```
````

## tTEscanR: first full review (new tracker, 2026-07)

_New tracker; follows the reviewer checklist template headings and quotes BiocCheck output._

````markdown
Thanks for your submission!

I’ll make a second round of review after the first comments below have been addressed.

## General package development

- [ ] Package passes `BiocCheck::BiocCheck()` when run on the source directory.

> ! WARNING: Provide a show() method for each S4 class • tTEscanR_Object

- [ ] `R CMD check --no-build-vignettes` within 10 minutes.

  - This takes ~ 11 min on my system. Please review how this can be optimized

- [ ] Undesirable files. System files like `.DS_Store`, `*.so`, etc. should not be included (see [.gitignore](https://contributions.bioconductor.org/gitignore.html) for a listing)

  - Should the `docs/` directory be included?

- [ ] Packages need to work with current version of Bioconductor and packages.

  - ggradar in not on CRAN or Bioconductor from what I can tell.

## Common Bioconductor Methods and Classes

- [ ] Reuse of [common Bioconductor methods and classes](https://contributions.bioconductor.org/reusebioc.html#reusebioc) when appropriate
- [ ] Indication of how package functionality can be integrated into a Bioconductor pipeline/workflow typically in vignette intro

## README file

- [ ] Include Bioconductor installation instructions

  - Please document how to install directly the package from Bioconductor (or GitHub for now if you wish) with BiocManager

## The DESCRIPTION file

- [ ] `Title` field.

  - What do you mean by “advanced” here?
  - What do you mean by “R-based package”? In opposition to just “R package”?

- [ ] `Authors@user-1` field.

  - You mention this is based on https://github.com/wgao688/sc_tRNA_mRNA. Is their license compatible with this reuse? Should they be included as an author?

- [ ] `Depends`, `Imports`, `Suggests`, `Enhances` fields.

  - Some dependencies in `Suggests` are used unconditionally in the code. Please move them to `Imports` (preferred solution) or use `requireNamespace()` to check for their presence before using them. For example: https://github.com/reviewer-2/tTEscanR/blob/d5854c30c1f67560bec105b714505983a0dfb35b/R/tTE_HelperFunctions_DEA.R or https://github.com/reviewer-2/tTEscanR/blob/d5854c30c1f67560bec105b714505983a0dfb35b/R/DifferentialExpressionAnalysis.R#L180-L183
  - If you turn `matrixStats` as an `Imports`, you are several opportunities to simplify your code by using its vectorized functions instead of `apply()` calls. Please review the code and see where you can replace `apply()` calls with `matrixStats` functions.

- [ ] It is strongly encouraged to include a `fnd` entry in Authors@user-1 with any relevant Grant Ids to trace funding activities. Do you have any funding to report?

## The NEWS file

- (Not mandatory) I recommend using `NEWS.md` rather than NEWS for nicer formatting capabilities

## Documentation

### Man Pages

- [ ] Please add an export to `getCodonFreq()`
- [ ] Please add a package-level man page. You do it with `usethis::use_package_doc()`.
- [ ] Please add the data source or reference in the bundled data.
- [ ] Please regenerate your man pages with `devtools::document()`

## Additional Comments or Concerns:

- It’s not necessary to include `as.character()` around numeric variable in `message()`. Dropping it will make the package more readable

- I believe this `for` loop can be dropped: https://github.com/reviewer-2/tTEscanR/blob/d5854c30c1f67560bec105b714505983a0dfb35b/R/CodonFreqPerGene.R and you can rely entirely on vectorized function calls (`paste()`, `grepl()`, `toupper()`, etc. are vectorized). Since you mention AI usage, you can ask it to vectorize the code for you if you’re not sure how to do it. It will be faster and more readable.

- Since you are doing a bit of string manipulation, it may be good to remember to use `fixed = TRUE` in `grepl()`, `grep()`, `strsplit()`, etc. when possible. The following command can help you find them all:

``` r
lintr::lint_package(".", linters = lintr::fixed_regex_linter())
```

- Is it really necessary to define your own colour palette? Did you verify that the colours are colour-blind friendly? https://github.com/reviewer-2/tTEscanR/blob/d5854c30c1f67560bec105b714505983a0dfb35b/data-raw/internal_data.R#L117-L131

- The package contains some typos. Please run it through a spell checker, such as https://cran.r-project.org/package=spelling, or any spell checker provided by your IDE.

- Are functions such as `savePlot()` really necessary? They don’t seem more user-friendly or powerful than the standard `ggsave()` function.

- Would it make sense to add this in your `style.css`? https://github.com/reviewer-2/tTEscanR/blob/d5854c30c1f67560bec105b714505983a0dfb35b/vignettes/tTEscanR_codonfreq_module.Rmd#L24-L44

## Plan for next round of review

- Review code in `R/` again.
- Review the vignettes again.
````

## tTEscanR: follow up (new tracker, 2026-10)

_New tracker; follows the reviewer checklist template headings and quotes BiocCheck output._

````markdown
Thanks for your work on this! The package is in much better shape and I think we're nearly there.

## General package development

- See PR https://github.com/submitter-2/tTEscanR/pull/2 for BiocCheck issue fix

## The DESCRIPTION file

- I am still a bit uncomfortable about the fact that this package is including code that didn't have an explicit license. Could you please reach out to the authors of https://github.com/wgao688/sc_tRNA_mRNA and ask them to include an explicit license in their repository?

## Documentation

### Vignette

- Could you please double check that you really `eval = FALSE` where you are using it? I understand the need for examples relying on biomaRt, but from a quick look, it seems you might be able to remove some of the `eval = FALSE` flags.

## Additional Comments or Concerns:

- You don't consistently use your `isTableLike()` helper. Should you? https://github.com/submitter-2/tTEscanR/blob/bf75b1ff98d4e905028bcba9e98e67f1004b3bc5/R/tTE_HelperFunctions_GeneralInternal.R#L146-L149

- This sprintf call is invalid. You cannot split the message into several arguments like this with sprintf: https://github.com/submitter-2/tTEscanR/blob/bf75b1ff98d4e905028bcba9e98e67f1004b3bc5/R/AAUsage.R#L132-L136

- It doesn't look like you're using the `getOutputName()` function anywhere.

- It would be nice to have a global option such as `tTEscanR.quiet` to control the verbosity of the package. On the same note, instead of the `if (verbose) message(...)` pattern, you could define a helper function such as `tTEscanR_message()` that checks the global option / value of the `verbose` argument and prints the message if appropriate. This would make the code cleaner and easier to maintain.

- This is not very helpful if you don't specify at least the source of the file: [`raw_data <- read.delim("/Users/anavaras/Downloads/tTEscanR_default_data/gencode.dmp",`](https://github.com/reviewer-2/tTEscanR/blob/d09f07802c738b41c945b7e9370ab786b89a716f/data-raw/internal_data.R#L13-L14). Ideally, you would even download the file directly in the script.

- Please avoid growing vectors in loops: https://github.com/reviewer-2/tTEscanR/blob/d09f07802c738b41c945b7e9370ab786b89a716f/R/GeneralProcessing.R#L42-L50. This results in inefficient code. Instead:
  - use `lapply()` or `vapply()`
  - pre-allocate a vector of the correct size and fill it in the loop
  - **if you really need to grow a vector in a loop**, use a `list()` (it can grow without performance issues) and `unlist()` at the end.
````

## ExCluster: first full review (legacy tracker, 2018-06)

_Legacy tracker; leads with fit/interoperability, then build report and file sections; two follow-ups._

````markdown
Thank you for your submission to Bioconductor. Please see the following points: 

**GENERAL**
- [ ] you are not Depending, Importing, or Suggesting any Bioconducotr packages.  There should be some interoperability with existing Bioconductor classes and methods for RNA-seq data. Especially GenomicRanges, SummarizedExperiment, and rtracklayer. See  http://bioconductor.org/developers/how-to/commonMethodsAndClasses/
  
- [ ] How does this differ from existing RNA-seq differential expression analysis.  Namely DESeq2, DEXSeq, and JunctionSeq


**BUILD REPORT**
Fix the following NOTES:
```
* checking DESCRIPTION meta-information ... NOTE
Malformed Title field: should not end in a period.
Package listed in more than one of Depends, Imports, Suggests, Enhances:
  'Rsubread'


* checking dependencies in R code ... NOTE
'library' or 'require' call to ‘Rsubread’ which was already attached by Depends.
  Please remove these calls from your code.

* checking R code for possible problems ... NOTE
for global functions and global variables.  
see  ?globalVariables
and suggest in NOTE about adding importFrom to NAMESPACE


* Checking unit tests...
    * NOTE: Consider adding unit tests. We strongly encourage them. See
      http://bioconductor.org/developers/how-to/unitTesting-guidelines/.

* Checking coding practice...
    * NOTE: Avoid 1:...; use seq_len() or seq_along() found in files:


* Checking formatting of DESCRIPTION, NAMESPACE, man pages, R source,
  and vignette source...
    * NOTE: Consider shorter lines; 371 lines (17%) are > 80 characters
      long.
    * NOTE: Consider multiples of 4 spaces for line indents, 17
      lines(1%) are not.
```

**DESCRIPTION**
- [ ]  remove LazyData: true . This rarely proves to be a good thing. In our
experience it only slows down the loading of packages with large data.
- [ ] Remove or relabel   Author: 2018-06-01
- [ ] Remove Type: Package  it is unnecessary

**NEWS** 
- [ ] Please properly format. Change `ExCluster Version 0.99 submission to
bioconductor!`  to `Changes in Version 0.99.0 `

**inst**
- [ ] include an inst/script/ directory that contains scripts and details of how
the data was generated in inst/extdata.  It should either be code or sudocode. 

**vignettes**
- [ ] Remove hidden files ._ExCluster.Rnw and ._ExCluster.pdf.  Also remove
ExCluster.pdf, ExCluster.synctex.gz, ExCluster.tex, and ExCluster_examples.R.
This directory really should only contain the ExCluster.Rnw 

- [ ] Add a Table of Contents

- [ ] Remove this line `when it asks you if you want to update [a/s/n] packages,
  type ’n’ and hit enter:`  Leave it up to the user if they want to update any
  packages. 

- [ ] Is there a reason you can't make the code robust enought to work with
  chromosomes specified as '1, 2, 3' instead of 'chr1, chr2, chr3' etc? 

 - [ ] Why is it limited to only 2 conditions for analysis? 

- [ ] In your toy example, you only need one `library(ExCluster)` call. 

- [ ] Reuse your data object.  It seems like you wouldn't need all the data -
  for example you supposely "flatten the GFT to GFF" in the first section of
  code, why not use this object rather than loading another system file
  "sub_gen.v23.ExClust.gff".  And similarly you just did the "process counts
  step" and generated a normCounts so you shouldn't have to load a system file
  "normCounts.txt"      
  The extdata included should be minimal and you should used the object created
  along the way rather than "reloading" system files. This doesn't seem
  currently possible as trying to use output from previous steps results in
  ERRORS - this makes me skeptical of the results that are generated along the
  way. 

- [ ] Do not right to the users system in test, examples, or vignettes.  Any
  output created should right to tempdir().  Always use tempdir() or tempfile()
  for output of test, examples, or vigenttes. 

- [ ] Would be great to show an example integrating with existing Bioconductor
  packages and classes. 


**man**
- [ ] Remove the hidden files.  ._ExCluster.Rd, ._GFF_convert.Rd,
._plotExonlog2FC.Rd,  and ._processCounts.Rd


**R Code**
GFF_convert.R

- [ ] Can rtracklayer and rtracklayer results be utilized for reading files?
  There already exists many import functions for different file types; use an
  existing rather than creating your own. You should be able to use minimally
  the results of rtracklayer or other Bicoonductor import methods for both GTF
  and GFF files in the rest of your code. 

- [ ] you are assuming a specific ordering of columns without actually checking
  this ordering is consistent and hard coding values in your code assuming
  this. (i.e number of columns 9 -  that the 9 columns are in the order of some
  'default format' ie. V7 is assumed +/- , v3 has 'exon')  -  perhaps this is ok
  but please elaborate why you can assume this? 

- [ ] You repeat the same code for gtf.plus and gtf.neg - take the repeated code
  and put into a helper function. We don't encourage large chunks of repeated
  code. 

**General Code comment:**

- [ ] Your code needs to be able to work with already existing Bioconductor
  infastructure for RNA-seq data. 

- [ ] can `for` loops can be more efficent with vapply? 


Please make corrections based on the above comments and comment back here with what has been updated and responses to clarification points above.  

Thank you.
````

## ExCluster: follow up (legacy tracker, 2018-06)

_Legacy tracker; leads with fit/interoperability, then build report and file sections; two follow-ups._

````markdown
Thank you for your updates a few additional comments:

**Build Report**
- [ ] Fix: NOTE: Avoid 1:...; use seq_len() or seq_along() found in files

**GFF_convert:**  
- [ ] Thank you for updating to use GenomicRanages intenrally however, the output of this function should be a GenomicRanges object as it represents Genomic positions. The mcols should be used to store additional information. 
- [ ] The repeated code has not been simplified as far as I can see. The main sections of repeated code for "Process +ve strand genes"  and "Now process -ve strand" remains. This code is highly similar except for the input that is used. This code should be its own function and then called for the + and for the -.  
- [ ]  If a user imports the gtf with rtracklayer, is there a way to do the bin reduction from this GenomicRanges object to be in the necessary format for your functions?  This would be the other interoperability we would like to see.

**You mentioned:**
```
8. I have also hard coded GFF columns, as our algorithm only accepts GFF files
produced by ExCluster. The GFF file format is more variable (GFF, GFF3,
etc.). However, only ExCluster produces GFF files with the information necessary
to conduct our analyses, and thus ExCluster tests to make sure that such a GFF
file is given.
```
- [ ]  But there does not seem to be a check that it is a GFF file produced with your GFF_convert function in either ExCluster.R or processCounts.R. If indeed it can only accept GFF that have been through your process than there should be a way to check for that. (Also this would be an example of a good unit test to add for proper output format from a function - or that your file.access function is
working properly)

```
7.  I have hard coded access GTF columns because these are very specific data
structures. For example, if column 7 does not equal the DNA strand in +/-
format, then the GTF file is corrupted or not read into R correctly, and should
not be used.
```
- [ ] I do not see this hard coded check for column specification assumingly in GFF_convert.R.  I only see a check that there are 9 columns -  if you really feel that this isn't necessary than that is okay but please confirm.    

**ExCluster.R**
-  [ ] The results of this function are also genomic coordinates;  the output therefore should be converted to GenomicRanges representation.


Please update with changes and comment back here when I should take another look. 
Cheers
````

## ExCluster: follow up (legacy tracker, 2018-08)

_Legacy tracker; leads with fit/interoperability, then build report and file sections; two follow-ups._

````markdown
Thank you for making these updates.  We really think it will enhance the usability of your package to be able to use the standard Bioconductor objects as input and output.  A few other points:

**vignette:**
In Details ExCluster Pipeline
Update the installation to use BiocManager instead of BiocInstaller 
```
if (!requireNamespace("BiocManager", quietly=TRUE))
    install.packages("BiocManager")
BiocManager::install("ExCluster")
```
Toy dataset
When I run  plotExonlog2FC  there are no results in the tempdir. 


**R Code:**
General:
- [ ] There are a few notes in the build report about seq_len or seq_along for 1:... 
- [ ] Use message instead of cat/print for printing output messages in code
- [ ] You can use rowMeans/colMeans and rowVars/colVars(fromlibrary(matrixStats)) instead of apply(matrix, 1, min).  It will greatly improve performance for computation over matrices. 
- [ ] There still is alot of repeated code in your functions. For example in
ExClust_main_function.R
There is a section  #### NOW RUN X MORE INTERATIONS IF'PVAL' ... - The code in these sections is the same except for a single variable NumIterations - The code in this section can be moved to a function that takes in the value that can be repeatedly called or have a switch statement that determines the input with one call to the function -  or some combination of both 

Please address the above issues and comment back here when you are ready for me to look at the package again. 
Cheers, 
Lori
````
