# How reviewers structure reviews

Written by the synthesis model from the computed statistics below and a sample of 357 per-comment structure records; the tables are computed directly. See `LEDGER.md` for method.

## First full reviews

**Typical skeleton**
1. Short greeting and thanks, sometimes with an apology for delay or a note on the package's overall state.
2. Sectioned findings, usually following the Bioconductor review template: general package development → common Bioconductor methods and classes → README → DESCRIPTION → NAMESPACE → NEWS/CITATION → documentation → vignette → man pages → package data → unit tests → R code → additional comments.
3. Closing request to respond point by point, bump the version, or ask questions. Many reviews have no sign-off at all.

**Sections in use**
- New tracker: R code 35%, documentation 31%, "the description file" 25%, general package development 25%, vignette 22%.
- Legacy tracker: description 47%, vignette 33%, namespace 31%, R 28%, R code 26%.
- Median length is about 3,000–3,400 characters with a median of 13 findings (see the comparison below).
- A minority of reviews skip headings entirely. They are free prose, or they open straight on the main concern, such as vignette clarity or coding style.

**Required vs suggested**
- Severity labels are common: *Important* vs *Note*, *Required* vs *Recommended* or *Suggestion*, or *must* vs *should*.
- Mandatory items are phrased as directives ("Please…", "must", "needs to").
- Optional items are hedged ("consider", "you may want to") or put as questions. Some say outright that the final decision is the author's.

**Checkboxes**
- Checkbox lists (`- [ ]`) are the dominant format in the new tracker (73% of first reviews) and common in the legacy tracker (47%).
- Numbered lists are rare in first reviews (4% new, 11% legacy).

**Tone**
- Polite and constructive, usually with brief praise before firm, specific requests.
- Requests are tied to guidelines, file names or line references.
- Some reviews are blunt, especially about vignette readability or coding style.

**Opening and sign-off phrasing**
- Openings: "Thank you for submitting your package to Bioconductor." "Thanks for your submission!" "Hi @user, thank you for your submission, and for your patience."
- Sign-offs: "Please try to answer the comments point by point when you are ready for a second review." "Let me know if you have any questions, I'll be happy to help!" A bare "Best," or "All the best," also appears.

## Follow-ups

**Typical skeleton**
1. Thanks for the changes, often with a status verdict ("nearly there", "still needs attention").
2. Remaining items, in short sections or a numbered list. Unaddressed points from the earlier review are restated.
3. Direct replies to the author's questions or pushback, including where the reviewer concedes a point.
4. Closing request: bump the version, push to trigger a new build, and comment back for re-review.

**Structure**
- Follow-ups are mostly free-form prose.
- Legacy follow-ups have low section use (vignette 10%, R code 8%), 23% checkboxes and 15% numbered items.
- New-tracker follow-ups reuse the template headings more (NAMESPACE file, documentation and R code at 29% each; README 24%), with 35% checkboxes.
- Follow-ups are shorter than first reviews, at a median of about 2,500–2,700 characters.

**Required vs suggested**
- Same markers as first reviews (*Important*/*Note*, *Required*/*Recommended*).
- Phrases such as "still", "not addressed" and "before acceptance" flag blocking items.
- "Totally up to you" or "you can incorporate these or not" flags optional ones.

**Tone**
- Appreciative opening, then firm and specific.
- Ranges from encouraging ("very close", "looks great") to terse or frustrated when issues recur.
- Often collegial and explanatory, with code examples.

**Opening and sign-off phrasing**
- Openings: "Thanks for the updates." "Thank you for making these changes."
- Sign-offs: "Please let me know when you have completed the revisions…" "Please address line-by-line for my next review." Or simply a first-name sign-off.

## New tracker vs legacy

- **Checkboxes:** more common in the new tracker, in first reviews (73% vs 47%) and follow-ups (35% vs 23%).
- **Numbered items:** less common in the new tracker, in first reviews (4% vs 11%) and follow-ups (6% vs 15%).
- **Section naming:** the new tracker uses the long template names, such as "the description file" (25%) and "general package development" (25%). The legacy tracker uses short names, such as "description" (47%), "r" (28%) and "man" (13%).
- **Length:** new first reviews are somewhat longer (median 3,386 vs 3,056 characters). Findings are the same at a median of 13.
- **Follow-ups:** new follow-ups are somewhat longer and carry more findings (2,684 vs 2,481 characters; 9 vs 6 findings). The new-tracker follow-up sample is small (n=17, vs 639 legacy), so treat this as tentative.
- **Other comments:** legacy "other" comments are mostly numbered (84%), have a median of 0 findings and are procedural or discussion posts. The new-tracker "other" sample (n=2) is too small to compare.

## Statistics

| Tracker | Kind | comments | checkboxes | numbered items | median chars | median findings |
|---|---|---|---|---|---|---|
| new | first_full_review | 101 | 73% | 4% | 3,386 | 13 |
| new | follow_up | 17 | 35% | 6% | 2,684 | 9 |
| new | other | 2 | 0% | 50% | 5,736 | 7 |
| legacy | first_full_review | 1,307 | 47% | 11% | 3,056 | 13 |
| legacy | follow_up | 639 | 23% | 15% | 2,481 | 6 |
| legacy | other | 367 | 0% | 84% | 1,739 | 0 |

Most common section labels, new tracker, first_full_review (share of comments):

`r code` 35%, `documentation` 31%, `the description file` 25%, `general package development` 25%, `vignette` 22%, `description` 17%, `vignettes` 16%, `additional comments or concerns` 14%, `man pages` 13%, `the namespace file` 12%, `namespace` 11%, `unit tests` 11%, `readme file` 11%, `common bioconductor methods and classes` 11%, `package data` 10%

Most common section labels, new tracker, follow_up (share of comments):

`the namespace file` 29%, `documentation` 29%, `r code` 29%, `readme file` 24%, `additional comments or concerns` 18%, `package data` 18%, `vignette` 18%, `the description file` 18%, `general package development` 18%, `description` 18%, `unit tests` 12%, `namespace` 12%, `vignettes` 12%, `the citation file` 12%, `common bioconductor methods and classes` 12%

Most common section labels, legacy tracker, first_full_review (share of comments):

`description` 47%, `vignette` 33%, `namespace` 31%, `r` 28%, `r code` 26%, `vignettes` 23%, `general package development` 15%, `man pages` 14%, `man` 13%, `documentation` 13%, `tests` 11%, `unit tests` 11%, `news` 11%, `general` 11%, `data` 8%

Most common section labels, legacy tracker, follow_up (share of comments):

`vignette` 10%, `r code` 8%, `description` 5%, `r` 4%, `man` 4%, `vignettes` 3%, `general` 3%, `general package development` 3%, `man pages` 3%, `unit tests` 2%, `namespace` 2%, `recommended` 2%, `documentation` 2%, `required` 2%, `news` 2%
