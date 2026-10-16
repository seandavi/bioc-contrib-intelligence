# Package-submission review automation: landscape (Oct 2026)

Researched 2026-10-16. Every claim carries a source URL. Anything marked **(inferred)** is my interpretation and not stated by the source. "Gate 1/2/3" refers to our design: Gate 1 is fit triage, Gate 2 is blockers only, Gate 3 is final fixes delivered as verifiable PRs.

## Summary

1. **Deterministic gates are universal. LLM gates are nearly absent.** Every ecosystem surveyed automates mechanical acceptance (R CMD check/BiocCheck, pkgcheck, Julia AutoMerge, `brew audit`, conda-forge lint, Spack checksums). None of them lets an LLM accept or reject a submission. In the one prototype that applies an LLM to Bioconductor (LiNk-NY/BiocReviews), the LLM rewrites findings that a rule-based stage already produced.
2. **"Fit" is mostly decided by cheap deterministic proxies plus a human.** Examples: Homebrew's notability check (≥75 stars, 30 forks or 30 watchers, repo at least 30 days old) is built into `brew audit`. JOSS requires at least 6 months of public history. Julia makes new packages wait 3 days for community comment and enforces name-distance rules. rOpenSci's `pkgmatch` finds overlapping packages, Bioconductor included. Nobody uses an ML classifier for fit. Our early result (DESCRIPTION-only triage barely beats grep) is consistent with this: the signals that work come from history and code.
3. **Bioconductor's new BiocContributions (2026) automates everything up to reviewer assignment.** Its own reviewer guide says the admin pre-check "will no longer occur," so fit judgement moved to the reviewer. This is exactly the gap a Gate 1 assist would fill.
4. **The best-measured automated pipeline is CRAN's.** In June 2018, 68.1% of 3,571 incoming actions were automatic, and every first-time submission still gets a manual inspection.
5. **Measured LLM-reviewer precision is modest.** CodeRabbit comments were accepted 36.4% of the time and rejected 56.3%. Qodo-based review at Beko had 73.8% of comments acted on, but PR close time rose. Google's AutoCommenter reached its 80% "useful" target only through **per-rule calibrated thresholds and suppression of noisy rules**, which is the same idea as Clef-style calibrated typed decisions.
6. **AI policies have converged on "allowed, disclosed, a human is responsible."** This holds for JOSS, rOpenSci, pyOpenSci, Bioconductor, Julia, Homebrew, Nixpkgs and Debian (GR 2026). Julia and Nixpkgs ban unreviewed "vibe-coded" contributions. JOSS raised its scope bar instead. CRAN's policy and conda-forge's docs had no AI text that I could find.
7. **Queue tooling exists but is shallow.** The rOpenSci dashboard tracks stage durations and editor load with red flags. Bots handle reminders (rOpenSci, JOSS `remind`). Bioconductor has stale or inactive workflows. No ecosystem publishes a "whose move is it" ball-in-court metric or reviewer-load-aware assignment. That is our opportunity.

---

## 1. R

### 1.1 rOpenSci software peer review

**What is automated, and at which stage**
- **Pre-submission and blockers:** `pkgcheck` combines `goodpractice` (R CMD check, coverage, lintr), `pkgstats` and rOpenSci structure checks. A package is ready only with "all ticks and no cross symbols". The checklist is generated at submission and editors use it to decide whether to process the package ([pkgcheck docs](https://docs.ropensci.org/pkgcheck/)). Authors can run the same checks on every push with [pkgcheck-action](https://github.com/ropensci-review-tools/pkgcheck-action).
- **Static code index:** `pkgstats` does "static code analyses for R packages" ([repo](https://github.com/ropensci-review-tools/pkgstats)) and requires ctags and GNU global ([pkgcheck docs](https://docs.ropensci.org/pkgcheck/)). This is the closest R analogue to our scip-r index **(inferred)**.
- **Statistical standards:** `srr` ("Software Review Roclets", [repo](https://github.com/ropensci-review-tools/srr)) has authors tag code with the standards each part meets. The bot command `check srr` verifies those tags ([editor guide](https://devguide.ropensci.org/softwarereview_editor.html); standards in the [stats dev guide](https://stats-devguide.ropensci.org/)).
- **Fit and overlap:** `pkgmatch` "find[s] R packages matching either descriptions or other R packages", using "text and code matching algorithms" against rOpenSci, CRAN or **Bioconductor** corpora ([repo README](https://github.com/ropensci-review-tools/pkgmatch)).
- **Editorial bot:** `@ropensci-review-bot` is built on Buffy ([ropensci-org/buffy](https://github.com/ropensci-org/buffy)). Its commands include `check package`, `assign @x as editor/reviewer`, `seeking reviewers`, `set due date`, `put on hold` (reminds editors every 90 days), `submit review <url> time <hours>` (logs reviewer effort), `approve`, and `out-of-scope` ([editor guide](https://devguide.ropensci.org/softwarereview_editor.html)).
- **AI agent assists (2026):** Experimental agent "skills" for preparing a package for review ([ropensci-skills](https://github.com/ropensci-review-tools/ropensci-skills)). A `goodpractice` skill tells an agent to edit code until goodpractice checks pass ([goodpractice4agents.md](https://github.com/ropensci-review-tools/goodpractice/blob/main/inst/skills/goodpractice4agents.md); announced in the [June 2026 news](https://ropensci.org/blog/2026/06/30/news-june-2026/)).

**Human role.** The handling editor runs the checks and must "aim to finish initial checks and start seeking reviewers within 5 working days". Two human reviewers are required, with a 21-day default due date and reminders at 1 and 2 weeks. A rotating Editor-in-Chief (about 3 months) triages scope ([editor guide](https://devguide.ropensci.org/softwarereview_editor.html)).

**AI policy (preliminary, 2026).** rOpenSci permits AI use in development and review, with disclosure and an affirmation that "all generated material has been carefully reviewed". It adds an editor-checklist item on whether the AI-use description is sufficient. Editors may judge whether there is enough human contribution, considering motivation, development history and design. Reviewers may use AI, but "all review text must reflect the judgement of the reviewer". The stated worries are that reviewers end up validating "largely AI-generated software" and that AI use could increase "the time to find reviewers". Disclosure is meant to direct reviewer attention, for example to AI-written tests ([blog, Feb 2026](https://ropensci.org/blog/2026/02/26/ropensci-ai-policy/)). The submission template gained an AI-use section in March 2026 ([news, Mar 2026](https://ropensci.org/blog/2026/03/30/news-mars-2026/)). There is no published outcome from an AI-in-review pilot yet.

**Queue metrics.** The [rOpenSci dashboard](https://dashboard.ropensci.org/) is updated daily. It has Editors (availability and portfolio), Software Review (open issues colour-coded by urgency, red when a stage is unusually long) and Historical Data ([history page](https://dashboard.ropensci.org/history.html)) sections. The EiC checks it weekly ([editor guide](https://devguide.ropensci.org/softwarereview_editor.html)).

**What to borrow:** pkgmatch (works on Bioc) as a Gate 1 overlap signal; `submit review … time <hours>` effort logging; one-comment checklists; the dashboard's per-stage "unusually long" flag; disclosure as a way to *route* reviewer attention.

### 1.2 CRAN

- **Pipeline:** Incoming packages "are automatically checked under both Linux and Windows". Clean packages with reverse dependencies go to a queue for automatic reverse-dependency checks. Well-established packages that pass cleanly can be published automatically. "inspect" triggers manual inspection, which "always" applies to first-time submissions. In June 2018 there were 2,122 submissions and 3,571 actions, 68.1% automatic and 31.9% manual ([R Journal, Changes on CRAN 2018-1](https://journal.r-project.org/news/RJ-2018-1-cran/)).
- **Queue visibility:** Folders (inspect, newbies, pretest, waiting…) are exposed by the community dashboard [cransays](https://github.com/r-hub/cransays) ([dashboard](https://r-hub.github.io/cransays/articles/dashboard.html)) and the [foghorn](https://www.r-bloggers.com/2021/07/foghorn-package-find-out-pending-cran-packages-in-the-pipeline/) package.
- **Policy:** "The time of the volunteers is CRAN's most precious resource" ([CRAN Repository Policy](https://cran.r-project.org/web/packages/policies.html)). A text search of that page on 2026-10-16 found **no mention of AI, LLMs or generative tools**.
- **What to borrow:** the explicit route vocabulary (publish / recheck / inspect / newbies). Measuring the automatic share of actions is a KPI we could report.

### 1.3 Bioconductor

- **BiocContributions (2026):** GitHub Actions plus R-universe replace the Single Package Builder, and the process "avoids administrative steps that have historically bottlenecked the review process" ([blog, 2026-06-15](https://blog.bioconductor.org/posts/2026-06-15-new-submission-process-with-Runiverse/)). The sequence is as follows ([submitters.md](https://github.com/Bioconductor/BiocContributions/blob/devel/docs/submitters.md)):
  1. A deterministic **precheck**: public GitHub URL, DESCRIPTION and vignettes present, Package/Version/biocViews, name matches the repo, version x.99.y, no Remotes or Additional_repositories, no file over 5 MB, no Git LFS, no duplicate submission. A failing issue is auto-closed with reasons.
  2. The submitter comments `/accept-policies`, which adds the `pre-review` label.
  3. The package is staged to BiocStaging and R-universe, and a build report (BiocCheck plus multi-platform R CMD check) is posted with Build OK/Note/Warning/Error labels.
  4. "Bioconductor will not assign a reviewer to a package until ERRORs are resolved".
  5. Review "typically within 3 weeks of a clean build".
  6. Labels for accepted, declined or inactive. **A decline requires a second reviewer to concur.**
- **Fit has shifted to reviewers:** "All previous administration steps are now automated up to assigning the reviewer… Some pre-check that admins would formerly do will no longer occur. You as a reviewer should use your best judgement if a package is appropriate for Bioconductor" ([reviewers.md](https://github.com/Bioconductor/BiocContributions/blob/devel/docs/reviewers.md)). Workflows include `check-stale-reviews`, `inactive-review`, `manually-assign-reviewer`, `decline-package` and `confirm-decline` ([workflows dir](https://github.com/Bioconductor/BiocContributions/tree/devel/.github/workflows)). As of the version I read, `check-stale-reviews` was `workflow_dispatch` only (manually triggered), not scheduled.
- **AI and third-party code policy:** A non-trivial AI-generated or copied portion must be discussed in the issue and disclosed in the PR (e.g. "Assisted-by: Name of AI"), with provenance cited and license compatibility confirmed. The submitter remains responsible ([contributions guide ch. 19](https://contributions.bioconductor.org/ai-policy-third-party.html)). That page gives reviewers no specific duties.
- **LiNk-NY/BiocReviews** ("AI-assisted Prototype for Reviewing R / Bioconductor Packages", [repo](https://github.com/LiNk-NY/BiocReviews)) is a two-stage pipeline.
  - **Stage 1** (`generate_review.R`) is rule-based. It runs over R CMD check, BiocCheck and coverage output, with no API.
  - **Stage 2** sends the static review, raw artifacts, DESCRIPTION, NAMESPACE and `R/*.R` (100k-char budget, smallest files first) to an LLM. The default model is `gemini-3.1-pro-preview`, with GitHub Models `gpt-4o` as an alternative, and a guidelines file is prepended. The LLM "re-organises findings, prioritises required fixes".
  - Prompts are hard-truncated at 120k characters with a visible warning.
  - It is triggered when a collaborator adds an `AI review` label or comments `@biocreview`. The output is framed as "preliminary assessments that assist human reviewers".
  - It also stores a corpus of human reviews (`packages/`).
- **Bioconductor/BiocPkgReviewer** (private; per our project context): 7 Claude Opus passes per package, about $8 per review notional.
- **What to borrow:** the precheck's auto-close-with-reasons pattern; the two-reviewer decline rule (a human check on negative decisions); BiocReviews' human-review corpus as labelled data.

### 1.4 Other R-specific LLM tooling

No R tool was found that performs CRAN- or Bioc-style submission review with an LLM, other than BiocReviews. Adjacent tools: `ellmer` ([Posit](https://posit.co/blog/announcing-ellmer)) as an LLM client, and `chores` (LLM code-rewrite assistants, [README](https://cran.r-project.org/web/packages/chores/readme/README.html)).

---

## 2. Python

### 2.1 pyOpenSci

- **Process:** The EiC posts one checklist comment covering install (PyPI or conda), import, **fit and overlap**, docs, license, CI tests and so on, then assigns an editor. Scope concerns go to editors on Slack. The checklist includes "The package authors have disclosed the use of Generative AI tools". EiC follow-up starts after 3–4 weeks of inactivity, and escalation after more than a month ([EiC guide](https://www.pyopensci.org/software-peer-review/how-to/editor-in-chief-guide.html)).
- **Automation:** Mostly human. `pyosmeta` parses review issues to maintain contributor and review metadata ([PyPI](https://pypi.org/project/pyosmeta)). I found no pkgcheck-equivalent bot. There is a third-party [review dashboard](https://dashboard.thecoatlessprofessor.com/pyopensci-software-review) with stage durations (snapshot: 176 submissions, 26 active).
- **AI policy:** Disclosure, not prohibition. The motivation is that GenAI "strains volunteer peer review programs" ([policy blog PR #734](https://github.com/pyOpenSci/pyopensci.github.io/pull/734)).
- **Astropy affiliated packages** now go through pyOpenSci review with Astropy editors participating (APE 22, Jan 2024; old registry frozen Mar 2024) ([astropy.org/affiliated](https://astropy.org/affiliated); [pyOpenSci discourse](https://pyopensci.discourse.group/t/astropy-partnership-next-steps/432)). This **partner model**, with a domain community running fit on top of a generic review, is relevant to Bioc sub-communities.

### 2.2 PyPI (no review; supply-chain automation)

- Over 2,000 malware reports in 2025: "66% … handled within 4 hours", 92% within 24 hours. PyPI "now automatically detects and flags potential typosquatting attempts during project creation". Over 50,000 projects use trusted publishing (more than 20% of uploads), and 17% of uploads carry attestations ([PyPI 2025 review](https://blog.pypi.org/posts/2025-12-31-pypi-2025-in-review)).
- Quarantine is an admin action that makes a project hard to install ([blog 2024-12-30](https://blog.pypi.org/posts/2024-12-30-quarantine/)). Reports arrive through a web button and a trusted-reporter API ([blog 2024-03-06](https://blog.pypi.org/posts/2024-03-06-malware-reporting-evolved/)). PSF minutes say automated quarantine worked "without false positives" ([2025-09-10](https://www.python.org/psf/records/board/minutes/2025-09-10/)).
- **Borrow:** trusted-reporter signals and time-to-action SLOs as queue metrics.

### 2.3 conda-forge staged-recipes

- **Automation:** A linter workflow runs on every PR (with a read-only token, since it may `eval` untrusted code) and CI builds on several OSes ([workflows](https://github.com/conda-forge/staged-recipes/tree/main/.github/workflows)). Recipes are generated by tools like grayskull and then reviewed by humans ([docs](https://conda-forge.org/docs/maintainer/understanding_conda_forge/staged_recipes/)).
- **Routing:** **language-specific review teams** (`@conda-forge/help-r`, `help-python`, …). A bot labels the PR `review-requested` when a team is pinged, and first-time contributors can ask a bot to ping. The template says "Review times … may be days or weeks" ([PR template](https://github.com/conda-forge/staged-recipes/blob/main/.github/pull_request_template.md)). The checklist is deterministic and policy-focused: license packaged, no vendoring, tarball source, build number 0.
- **AI policy:** none found (GitHub code search of conda-forge docs and staged-recipes, 2026-10-16).
- **Borrow:** route by expertise label; let a bot add `review-requested` when the submitter explicitly hands off. This is a clean "ball-in-court" event.

---

## 3. Other ecosystems

### 3.1 Julia General registry (RegistryCI / AutoMerge)

This is the closest analogue to gated automated acceptance.
- **Automated guidelines for new packages:**
  - Name rules: at least 5 characters, no "julia" in the name, **Damerau–Levenshtein distance ≥3** from existing names, lowercase distance ≥2, visual distance above 2.5.
  - Version and compat rules: upper-bounded `[compat]`, sequential versions.
  - Loadability: installable and importable, with an OSI license.
  - Source: [AutoMerge guidelines](https://juliaregistries.github.io/RegistryCI.jl/stable/guidelines/).
- **Waiting periods:** 3 days for new packages ("allows time for community feedback"), 15 minutes for new versions ([General README](https://github.com/JuliaRegistries/General/blob/master/README.md)). The 3 days are used to check that the name is appropriate, the package is "functional and non-empty", the code is not malicious, and docs exist (same README).
- **Human in the loop:**
  - **Any comment blocks AutoMerge** unless it contains `[noblock]`.
  - Overrides are **labels** (`Override AutoMerge: name similarity is okay`).
  - Early merges get "stricter standards" from a registry maintainer.
  - Out-of-guideline exceptions set no precedent.
  - Sources: [README](https://github.com/JuliaRegistries/General/blob/master/README.md); [guidelines](https://juliaregistries.github.io/RegistryCI.jl/stable/guidelines/).
- **AI policy:** LLM *assistance* is fine. "Vibe-coded" packages (generated "without human review") are not suitable. Packages with "obvious signs of 'AI slop'" "may be blocked". Substantial AI contributions are disclosed in the README. Communication must be the author's own ("Don't rely on an LLM to think for you") ([README](https://github.com/JuliaRegistries/General/blob/master/README.md)).
- **Borrow:** a passive acceptance window where silence means pass and any human comment blocks; label-based overrides; deterministic name-similarity checks.

### 3.2 JOSS (editorialbot / Buffy)

- **Bot:** Built on [Buffy](https://github.com/openjournals/buffy). `check repository` reports authorship, languages (cloc), word count, license and a "Statement of need" section. `check references` validates DOIs. Other commands are `query scope`, `remind @user in <time>`, `recommend-accept`, and EiC-only `accept`/`reject` ([editorialbot docs](https://joss.readthedocs.io/en/latest/editorial_bot.html)).
- **Scope triage:** In 2020, submissions under 1,000 LOC were flagged for scope and those under 300 were desk-rejected ([blog 2020](https://blog.joss.theoj.org/2020/07/minimum-publishable-unit)). In 2026, JOSS replaced the "three months of developer time" effort proxy, because AI makes code in "three days" or "three hours". It now weighs research impact, design thinking and open practices, and requires **at least 6 months of public history**. Projects with weeks of history get extra scrutiny ([blog Jan 2026](https://blog.joss.theoj.org/2026/01/preparing-joss-for-a-generative-ai-future)).
- **AI policy:** An AI usage disclosure section is mandatory. Incomplete disclosure can lead to anything "from desk rejection to institutional notification". Reviewers may use AI only for non-substantive tasks, and "All evaluative decisions … must come from human reviewer judgment alone" ([policies](https://joss.readthedocs.io/en/latest/policies.html)).
- **Queue:** There is an editor dashboard of assigned papers. Editors prompt after 7–10 days of silence ([editing guide](https://joss.readthedocs.io/en/latest/editing.html)). JOSS once ran a "reduced service mode" that capped new papers per week ([blog 2020](https://blog.joss.theoj.org/2020/05/reopening-joss)).
- **Borrow:** deterministic history proxies (repo age, commit span, contributor count) as Gate 1 features; `remind @user in <time>`.

### 3.3 Homebrew core

- **Deterministic fit check in code:** `brew audit` flags "GitHub repository not notable enough" (<30 forks, <30 watchers and <75 stars; the thresholds are tripled for self-submissions) and "GitHub repository too new (… 30 days required)" ([shared_audits.rb](https://github.com/Homebrew/brew/blob/master/Library/Homebrew/utils/shared_audits.rb); [Acceptance Policy](https://docs.brew.sh/Package-Acceptance-Policy)). New formulae are held to a higher bar than updates.
- **AI policy (strictest on process):**
  - Disclose the tool and model.
  - Review all output before asking for review.
  - **Do not** credit AI in commit trailers (`Assisted-by` is forbidden).
  - Answer reviewers without AI.
  - **Non-maintainers may have only one AI-assisted PR open at a time.**
  - Sources: [CONTRIBUTING](https://github.com/Homebrew/brew/blob/master/CONTRIBUTING.md); [Responsible AI Usage](https://docs.brew.sh/Responsible-AI-Usage).
- **Borrow:** encode "fit" heuristics as auditable code with self-submission multipliers; concurrency limits on AI-assisted submissions.

### 3.4 Nixpkgs

- **Automation:** ofborg's evaluation was migrated to GitHub Actions ([discourse](https://discourse.nixos.org/t/infrastructure-announcement-the-future-of-ofborg-your-help-needed/56025)). [nixpkgs-review](https://github.com/Mic92/nixpkgs-review) builds every reverse dependency of a PR locally. `nixpkgs-merge-bot` lets a **package maintainer** (not only a committer) merge, but only when the author is the update bot r-ryantm or a committer and the package is in `pkgs/by-name` ([CONTRIBUTING](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md)).
- **Gate 3 analogue:** "committers are encouraged to checkout the PR and push directly to the contributor's branch" for trivial fixes (same CONTRIBUTING). Latency is acknowledged openly: PRs may sit "days, weeks or sometimes even months".
- **AI policy:** "responsible person in the loop", disclosure required, an `Assisted-by:` trailer with tool and model **required**, "vibe coding without review is not permitted", and violations may be closed ([CONTRIBUTING §Automation/AI policy](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md)). The policy is still contested ([discourse](https://discourse.nixos.org/t/llms-in-nixpkgs/78964)).
- **Borrow:** scoped merge rights (low-risk change class plus trusted author plus owner) as a model for auto-accepting Gate 3 fix PRs; reviewers pushing fixes directly.

### 3.5 Debian NEW queue (ftp-master)

- Manual review by the FTP team, which is the only group that can accept or reject NEW packages ([LWN](https://lwn.net/Articles/884301/)). The main focus is `debian/copyright` and licensing. Lintian helps but is rarely a reason to reject ([REJECT-FAQ](https://ftp-master.debian.org/REJECT-FAQ.html); [Ubuntu AA guide](https://documentation.ubuntu.com/project/maintainers/AA/aa-new-review)). The public queue page lists age per package ([NEW queue](https://ftp-master.debian.org/new.html)).
- **AI policy:** A 2026 General Resolution chose "Responsible Use of Generative AI". Disclosure is encouraged, not required. Contributors stay fully accountable. Large-scale or automated changes require prior discussion. A strict ban lost ([vote 2026/002](https://www.debian.org/vote/2026/vote_002)).

### 3.6 Spack

- Reviewer guide with deterministic prechecks: `spack ci verify-versions` checksums, `@spackbot fix style`, `@spackbot run pipeline`. Maintainers confirm builds. "Packages are rarely inappropriate" ([package review guide](https://spack.readthedocs.io/en/latest/package_review_guide.html)). No AI policy found. A 2026 GSoC idea explores GenAI-assisted testing of package stacks ([HSF](https://hepsoftwarefoundation.org/gsoc/2026/proposal_Spack_AIAssistedTesting.html)).
- **Borrow:** bot commands that *apply* mechanical fixes (style) rather than comment on them, which is Gate 3 in miniature.

### 3.7 crates.io and npm (no review; supply chain only)

- **crates.io:** Malicious crates are removed after reports, for example from Socket ([2025-09-24](https://blog.rust-lang.org/2025/09/24/crates.io-malicious-crates-fasterlog-and-asyncprintln)). Since February 2026 each removal gets a RustSec advisory instead of a blog post ([2026-02-13](https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update)).
- **npm:** OIDC trusted publishing has been GA since 2025-07-31 ([changelog](https://github.blog/changelog/2025-07-31-npm-trusted-publishing-with-oidc-is-generally-available/)). After Shai-Hulud, GitHub announced 2FA for local publishing and short-lived tokens ([Help Net Security](https://www.helpnetsecurity.com/2025/09/23/npm-publishing-security-improvements/)).
- **Relevance:** low for fit review. Name-confusion checks (finch vs finch-rust) mirror Julia's distance rules.

---

## 4. AI/LLM-assisted code review generally

| System / study | Setting | Measured outcome | Lesson for us |
|---|---|---|---|
| Google **AutoCommenter** ([arXiv 2405.13565](https://arxiv.org/html/2405.13565v1)) | LLM flags best-practice violations with a URL to the rule; tens of thousands of developers | "Useful" ratio plateaued at about 54–60%. Reached the 80% target only after **per-URL (per-rule) thresholds** and **suppressing 17+5 noisy rules**. Estimated resolution about 40%. No significant change in review duration. Covered 68% of the best-practice URLs human reviewers cited; 66% of its top rules lie beyond static analysis | Calibrate *per check type*, prune checks with low precision, and value precision over recall to protect trust. This is exactly how Clef typed questions should be run |
| **Qodo PR-Agent at Beko** ([arXiv 2412.18531](https://arxiv.org/abs/2412.18531v2), ICSE-SEIP 2025) | 4,335 PRs, 1,568 with automated review | 73.8% of comments resolved. PR closure time **rose** from 5h52m to 8h20m. Complaints of faulty, irrelevant or too frequent comments | LLM comments add work. Fewer, blocker-only comments (Gate 2) are the right shape |
| **CodeRabbit in the wild** ([arXiv 2607.03316](https://arxiv.org/abs/2607.03316)) | 31,073 comments, 239 repos | 36.4% accepted, 56.3% rejected (false positives, redundant, out-of-scope). Lightweight learned models predicted rejection with **F1 up to 76%** | A cheap classifier can filter LLM output before humans see it |
| **GitHub ReviewBench** ([blog 2026-10](https://github.blog/ai-and-ml/reviewbench-an-open-benchmark-for-ai-code-review/); [review-bench.ai](https://review-bench.ai/)) | 219 PRs, golden set from humans, follow-up commits, static analysis and LLMs; LLM judge | Grounded and augmented precision and recall, plus Fβ. Judge agreement with senior engineers 96.6%. Copilot ensemble online: precision +8%, recall +13.6%, cost −8% | Build a frozen gold set from *follow-up commits* (we have version bumps after review comments) and report grounded recall |
| **Copilot code review** ([docs](https://docs.github.com/en/copilot/how-tos/agents/copilot-code-review/using-copilot-code-review)) | Leaves "Comment" reviews that don't count toward approvals. A Sep 2026 preview lets admins allow scoped approvals (secondary source: [startdebugging](https://startdebugging.net/2026/09/copilot-code-review-can-now-approve-pull-requests/)) | n/a | Even vendors keep approval off by default and scoped |
| **LLM review of research or scientific code** | No direct evaluation found. Adjacent: LLMs as manuscript "quality checkers" ([arXiv 2505.23824](https://arxiv.org/abs/2505.23824v2)); LLM-REVal on reviewer trust ([arXiv 2510.12367](https://arxiv.org/pdf/2510.12367)); "code-first peer review" vision ([arXiv 2606.07683](https://arxiv.org/pdf/2606.07683)) | n/a | Gap: nobody has benchmarked LLM review against domain package reviews. The BiocReviews human-review corpus plus the BiocContributions history could be the first such benchmark **(inferred)** |
| **Triage classifiers / slop detection** | Rule-scored GitHub Actions ([anti-slop](https://gittrend.io/repo/peakoss/anti-slop), [slopper](https://github.com/sloppers/slopper)). DFG project SpamPR-Buster (2026–29) plans an ML classifier ranking PRs ([HU Berlin](https://www.hu-berlin.de/en/forschungsinformationssystem/projekt-details/spampr-buster-bekaempfung-von-spam-pull-requests)) | No published registry-side accuracy found | Calibrated fit or triage classifiers for package registries are essentially unexplored |
| **Code-intelligence for review** | Sourcegraph positions its SCIP code graph as shared agent context ([Sourcegraph](https://sourcegraph.com/resources/context-compare)). Tree-sitter "blast radius" graphs for review exist as MCP tools (e.g. [repograph](https://github.com/4ff4n/repograph)) | No evaluation found | Structural indexes are used for *context selection*, not as decision features. Using scip-r facts as typed features is novel **(inferred)** |

---

## 5. AI-policy comparison

| Community | Stance | Disclosure | Notable specifics | Source |
|---|---|---|---|---|
| rOpenSci | Allowed (preliminary) | Template section; affirm review | Editors judge human contribution; reviewers may use AI, judgment must be theirs | [blog](https://ropensci.org/blog/2026/02/26/ropensci-ai-policy/) |
| pyOpenSci | Allowed | Required (EiC checklist) | Motivated by reviewer strain | [EiC guide](https://www.pyopensci.org/software-peer-review/how-to/editor-in-chief-guide.html) |
| JOSS | Allowed | Mandatory paper section | 6-month public history; reviewers' evaluative judgments human-only; false disclosure can mean desk rejection | [policies](https://joss.readthedocs.io/en/latest/policies.html), [blog](https://blog.joss.theoj.org/2026/01/preparing-joss-for-a-generative-ai-future) |
| Bioconductor | Allowed | Issue and PR disclosure, "Assisted-by" | Provenance and license; submitter responsible | [ch. 19](https://contributions.bioconductor.org/ai-policy-third-party.html) |
| CRAN | None found | — | Policy text has no AI mention (checked 2026-10-16) | [policy](https://cran.r-project.org/web/packages/policies.html) |
| Julia General | Assistance OK; vibe-coded not | README if substantial | "AI slop" may be blocked; no LLM replies to feedback | [README](https://github.com/JuliaRegistries/General/blob/master/README.md) |
| Homebrew | Allowed with limits | Required in PR | No AI commit trailers; one AI PR at a time; no AI replies | [CONTRIBUTING](https://github.com/Homebrew/brew/blob/master/CONTRIBUTING.md) |
| Nixpkgs | Allowed with human in loop | Required, `Assisted-by:` trailer | No vibe coding; violations closable | [CONTRIBUTING](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md) |
| Debian | Allowed (GR 2026) | Encouraged | Full accountability; automated mass changes need discussion | [vote](https://www.debian.org/vote/2026/vote_002) |
| conda-forge, Spack | None found | — | — | searched 2026-10-16 |

---

## 6. Queue, latency and reviewer load

| Community | Public metrics | Nudging / reassignment |
|---|---|---|
| rOpenSci | [Dashboard](https://dashboard.ropensci.org/): stage colour-coded by duration, editor availability and portfolio, historical durations, reviewer hours logged by bot | 1- and 2-week reminders; reassign after 3 weeks; editor load cap of about 1 per quarter and 4 per year; EiC weekly sweep ([guide](https://devguide.ropensci.org/softwarereview_editor.html)) |
| pyOpenSci | Third-party [dashboard](https://dashboard.thecoatlessprofessor.com/pyopensci-software-review) | EiC monthly sweep; Slack at 3–4 weeks; escalation ladder |
| JOSS | Per-editor dashboard; reviewer management app | `remind @user in <time>`; prompt at 7–10 days |
| CRAN | [cransays](https://r-hub.github.io/cransays/articles/dashboard.html) folder snapshot | n/a |
| Bioconductor | None public (labels only) | `check-stale-reviews` (manual dispatch); `inactive review` label closes; "3 weeks of a clean build" target |
| conda-forge | None | Team ping leads to a `review-requested` label; Zulip |
| Debian | [NEW queue](https://ftp-master.debian.org/new.html) with ages | n/a |
| Julia | n/a (bot-merged) | Silence means auto-merge after 3 days |

---

## 7. Comparison table (ecosystem × stage × automation × human role × AI policy)

| Ecosystem | Pre-submission | Triage / fit | Blockers | Polish / final | Post-acceptance | Det. vs ML/LLM | Human role | AI policy |
|---|---|---|---|---|---|---|---|---|
| **Bioconductor** (BiocContributions) | R-universe action for authors | Precheck (structural); fit is reviewer judgement | BiocCheck plus R CMD check; no reviewer until ERRORs fixed | Reviewer comments; version bumps | Daily builds | Deterministic; LLM only in BiocReviews and BiocPkgReviewer prototypes | 1 reviewer; 2 to decline | Disclose, responsible |
| **rOpenSci** | pkgcheck-action, ropensci-skills | EiC plus pkgmatch overlap | pkgcheck ✗ items | 2 reviewers, srr standards | Badge, registry | Deterministic; agent skills for authors | Editor plus 2 reviewers | Preliminary: disclose |
| **CRAN** | — | Newbies → manual inspect | Auto-check Linux/Win plus revdeps | Human emails | Daily checks, archival | Deterministic | CRAN team | None found |
| **pyOpenSci / Astropy** | — | EiC checklist (fit, overlap) | Manual checklist | 2 reviewers; partner criteria | JOSS fast-track | Mostly manual | EiC, editor, reviewers | Disclose |
| **JOSS** | — | Bot repo stats plus 6-month history; `query scope` | — | Reviewers' checklist | DOI, archive | Deterministic bot | EiC plus reviewers | Mandatory disclosure; human-only judgement |
| **Julia General** | — | Name-distance and 3-day window (comment blocks) | AutoMerge guidelines | — | TagBot | Deterministic | Optional; label overrides | Vibe-coded not allowed |
| **Homebrew** | `brew audit --new` | Notability and age audit | CI bottles | Maintainer review | Autobump | Deterministic | Maintainers | Disclose; 1 AI PR |
| **conda-forge** | grayskull | Team routing | Linter plus CI | Team review | Bots maintain feedstock | Deterministic | Language teams | None found |
| **Nixpkgs** | nixpkgs-review | — | CI eval/build | Committers push fixes | r-ryantm updates plus merge-bot | Deterministic | Committers, maintainers | Assisted-by required |
| **Debian** | lintian | FTP team | Copyright review | — | — | Mostly manual | FTP masters | GR: responsible use |
| **Spack** | spack audit/style | Rarely inappropriate | verify-versions, CI pipeline | `@spackbot fix style` | — | Deterministic | Reviewers, maintainers | None found |
| **PyPI / crates / npm** | Trusted publishing | Typosquat flagging | Malware reports → quarantine | — | Advisories | Deterministic plus reporter heuristics | Admins | n/a |

---

## 8. Synthesis

### (a) Recurring patterns

1. **Deterministic first, human decides.** Every system gates on cheap, explainable checks. No community delegates accept or reject to ML or an LLM. JOSS explicitly forbids AI evaluative judgements.
2. **Fit relies on *external* evidence, not prose.** Examples: notability (Homebrew), public history length (JOSS), community comment window (Julia), overlap search (pkgmatch, pyOpenSci "best in class"). Descriptions alone are rarely trusted.
3. **Negative decisions get extra friction**: Bioc's two-reviewer decline, Julia's "any comment blocks", rOpenSci's editor discussion for edge cases.
4. **The bot is a command interface over labels and state** (Buffy-based bots, BiocContributions label-triggered Actions, `@spackbot`). The state machine *is* the label set.
5. **AI policy = disclosure + responsibility + human communication.** The strictest communities (Homebrew, Nixpkgs, Julia) also regulate *communication* (no LLM replies) and *volume* (one AI PR at a time).
6. **LLM reviewers need calibration to be tolerated.** Raw acceptance rates are 36–74%. Usefulness rises when per-rule thresholds and suppression are applied (AutoCommenter).

### (b) Our Gate 1/2/3 versus practice

- **Matches.** Gate 2 "blockers only" matches the Bioc rule "no reviewer until ERRORs resolved", pkgcheck's ✗ semantics and the CRAN auto-check. Using deterministic BiocCheck and R CMD check as the backbone matches every ecosystem. Calibrated typed decisions (Clef) match AutoCommenter's per-rule thresholds conceptually.
- **Departs (forward).** Gate 1 as a *model-assisted* fit triage has no precedent. Everyone else uses deterministic proxies or human EiCs. BiocContributions just removed admin pre-checks, so the slot is open.
- **Departs (forward).** Gate 3 "final fixes as verifiable PRs" goes beyond practice. The nearest analogues are Nixpkgs committers pushing to contributor branches, `@spackbot fix style`, and rOpenSci's goodpractice agent skill (author-side).
- **Risk.** Practice suggests the human must own the Gate 1 *decision*. Our output should be a ranked, evidenced recommendation, with declines needing human concurrence (as in Bioc), not an auto-close **(inferred)**.

### (c) Ideas worth borrowing, ranked

1. **Add history and notability features to Gate 1.** Use repo age, commit span, number of contributors, stars/forks, prior releases and issue activity (Homebrew audit, JOSS 6-month rule), alongside scip-r code facts. This directly addresses "DESCRIPTION barely beats grep". These are cheap, deterministic and explainable.
2. **Calibrate per question and prune by measured precision (AutoCommenter).** Give each Clef typed question its own threshold from a validation set. Suppress questions whose precision is below target, and report per-question usefulness from reviewer feedback.
3. **Run overlap detection against Bioconductor (`pkgmatch` or our own scip-r symbol overlap)** as a Gate 1 feature, answering "novel concepts not already introduced" from reviewers.md.
4. **Ball-in-court state from explicit hand-off events.** Combine conda-forge's `review-requested` on ping, Bioc's version-bump-triggered builds and rOpenSci's stage labels into a "whose move" metric. Add rOpenSci-style red flags for "unusually long", per stage.
5. **A passive acceptance window with comment-to-block semantics (Julia) for Gate 2 clearance.** When deterministic checks are clean and Gate 1 is high-confidence, the reviewer has a fixed window to object. Silence advances the issue to in-depth review, never to acceptance.
6. **Build a gold set from follow-up commits (ReviewBench style).** Bioc review threads followed by version bumps give grounded labels for which comments mattered. Use them to evaluate both Clef gates and the 7-pass Opus reviewer for grounded recall per dollar.
7. **Use a cheap rejection-predictor filter on generated comments** (CodeRabbit study: F1 up to 76%) before showing LLM output to reviewers or authors. Fewer, better comments avoid the Beko-style slowdown.
8. **Log reviewer effort with a bot command** (`submit review … time <hours>`, rOpenSci) to measure reviewer load and the actual savings from gates.

### (d) Gaps nobody seems to address (opportunity)

- **Calibrated, evidence-cited fit triage** for a domain registry. Today it is either deterministic proxies or unstructured human judgement.
- **Code-structure features (SCIP/tree-sitter) as decision inputs.** Industry uses them only to select LLM context.
- **A ball-in-court latency metric and reviewer-load-aware assignment.** Dashboards show stage age, not who owes the next action, and no system balances assignment by measured load.
- **Benchmarks of LLM review against human reviews of *scientific packages*.** None found. Bioc has public review threads at scale.
- **Verifiable fix PRs from reviewers' requests (Gate 3).** Tools fix style mechanically, but nobody closes the loop from a reviewer comment to a CI-verified patch the author accepts.
- **Cost reporting.** No community publishes per-review LLM cost. A $/review versus grounded-recall curve, for example 7×Opus against gated Clef, would be new evidence.

---

## Sources

**R / rOpenSci / CRAN / Bioconductor**
- https://ropensci.org/blog/2026/02/26/ropensci-ai-policy/
- https://ropensci.org/blog/2026/03/30/news-mars-2026/
- https://ropensci.org/blog/2026/06/30/news-june-2026/
- https://devguide.ropensci.org/softwarereview_editor.html
- https://docs.ropensci.org/pkgcheck/
- https://github.com/ropensci-review-tools/pkgcheck-action
- https://github.com/ropensci-review-tools/pkgstats
- https://github.com/ropensci-review-tools/srr
- https://stats-devguide.ropensci.org/
- https://github.com/ropensci-review-tools/pkgmatch
- https://github.com/ropensci-review-tools/ropensci-skills
- https://github.com/ropensci-review-tools/goodpractice/blob/main/inst/skills/goodpractice4agents.md
- https://github.com/ropensci-org/buffy
- https://dashboard.ropensci.org/ , https://dashboard.ropensci.org/history.html
- https://journal.r-project.org/news/RJ-2018-1-cran/
- https://cran.r-project.org/web/packages/policies.html
- https://github.com/r-hub/cransays , https://r-hub.github.io/cransays/articles/dashboard.html
- https://www.r-bloggers.com/2021/07/foghorn-package-find-out-pending-cran-packages-in-the-pipeline/
- https://blog.bioconductor.org/posts/2026-06-15-new-submission-process-with-Runiverse/
- https://github.com/Bioconductor/BiocContributions/blob/devel/docs/submitters.md
- https://github.com/Bioconductor/BiocContributions/blob/devel/docs/reviewers.md
- https://github.com/Bioconductor/BiocContributions/tree/devel/.github/workflows
- https://contributions.bioconductor.org/ai-policy-third-party.html
- https://github.com/LiNk-NY/BiocReviews
- https://posit.co/blog/announcing-ellmer , https://cran.r-project.org/web/packages/chores/readme/README.html

**Python**
- https://www.pyopensci.org/software-peer-review/how-to/editor-in-chief-guide.html
- https://github.com/pyOpenSci/pyopensci.github.io/pull/734
- https://pypi.org/project/pyosmeta
- https://dashboard.thecoatlessprofessor.com/pyopensci-software-review
- https://astropy.org/affiliated , https://pyopensci.discourse.group/t/astropy-partnership-next-steps/432
- https://blog.pypi.org/posts/2025-12-31-pypi-2025-in-review
- https://blog.pypi.org/posts/2024-12-30-quarantine/ , https://blog.pypi.org/posts/2024-03-06-malware-reporting-evolved/
- https://www.python.org/psf/records/board/minutes/2025-09-10/
- https://conda-forge.org/docs/maintainer/understanding_conda_forge/staged_recipes/
- https://github.com/conda-forge/staged-recipes/blob/main/.github/pull_request_template.md
- https://github.com/conda-forge/staged-recipes/tree/main/.github/workflows

**Other ecosystems**
- https://juliaregistries.github.io/RegistryCI.jl/stable/guidelines/
- https://github.com/JuliaRegistries/General/blob/master/README.md
- https://joss.readthedocs.io/en/latest/editorial_bot.html
- https://joss.readthedocs.io/en/latest/policies.html
- https://joss.readthedocs.io/en/latest/editing.html
- https://blog.joss.theoj.org/2026/01/preparing-joss-for-a-generative-ai-future
- https://blog.joss.theoj.org/2020/07/minimum-publishable-unit , https://blog.joss.theoj.org/2020/05/reopening-joss
- https://github.com/openjournals/buffy
- https://docs.brew.sh/Package-Acceptance-Policy , https://docs.brew.sh/Responsible-AI-Usage
- https://github.com/Homebrew/brew/blob/master/CONTRIBUTING.md
- https://github.com/Homebrew/brew/blob/master/Library/Homebrew/utils/shared_audits.rb
- https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md
- https://github.com/Mic92/nixpkgs-review
- https://discourse.nixos.org/t/infrastructure-announcement-the-future-of-ofborg-your-help-needed/56025
- https://discourse.nixos.org/t/llms-in-nixpkgs/78964
- https://ftp-master.debian.org/REJECT-FAQ.html , https://ftp-master.debian.org/new.html
- https://documentation.ubuntu.com/project/maintainers/AA/aa-new-review , https://lwn.net/Articles/884301/
- https://www.debian.org/vote/2026/vote_002
- https://spack.readthedocs.io/en/latest/package_review_guide.html
- https://hepsoftwarefoundation.org/gsoc/2026/proposal_Spack_AIAssistedTesting.html
- https://blog.rust-lang.org/2025/09/24/crates.io-malicious-crates-fasterlog-and-asyncprintln
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update
- https://github.blog/changelog/2025-07-31-npm-trusted-publishing-with-oidc-is-generally-available/
- https://www.helpnetsecurity.com/2025/09/23/npm-publishing-security-improvements/

**AI code review / research**
- https://arxiv.org/html/2405.13565v1 (AutoCommenter)
- https://arxiv.org/abs/2412.18531v2 (Automated Code Review in Practice)
- https://arxiv.org/abs/2607.03316 (CodeRabbit in the wild)
- https://github.blog/ai-and-ml/reviewbench-an-open-benchmark-for-ai-code-review/ , https://review-bench.ai/
- https://docs.github.com/en/copilot/how-tos/agents/copilot-code-review/using-copilot-code-review
- https://startdebugging.net/2026/09/copilot-code-review-can-now-approve-pull-requests/ (secondary)
- https://arxiv.org/abs/2505.23824v2 , https://arxiv.org/pdf/2510.12367 , https://arxiv.org/pdf/2606.07683
- https://www.hu-berlin.de/en/forschungsinformationssystem/projekt-details/spampr-buster-bekaempfung-von-spam-pull-requests
- https://github.com/sloppers/slopper , https://gittrend.io/repo/peakoss/anti-slop
- https://sourcegraph.com/resources/context-compare , https://github.com/4ff4n/repograph
