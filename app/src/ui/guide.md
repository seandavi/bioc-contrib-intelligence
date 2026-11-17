## What this is

Bioconductor Reviews shows reviewers and the core team where each open submission on
[Bioconductor/BiocContributions](https://github.com/Bioconductor/BiocContributions) stands:
whose move it is, how long it has waited, what changed since the reviewer last commented,
and what the build machines report now. On each submission it also offers a **co-reviewer**,
an AI assistant that helps you draft your review comment.

It reads the tracker; it doesn't replace it. The app never posts, assigns, labels, accepts or
declines anything. Reviews still happen on the GitHub issue, under your name.

**Signing in.** Everything except this page needs a GitHub sign-in. You get in if you have at
least one open review assignment on BiocContributions, or triage permission there (the core
team, shown as *Admin*). Reviewers see their own assignments; admins see every submission.

## How to get an AI-assisted review of a package assigned to you

1. Sign in with GitHub. You land on **My queue**: your assignments, the ones waiting on you first.
2. Click a package. The **review page** shows the conversation, the current checks and the
   version history.
3. Click **Co-review**. A panel opens with a chat on top and your **draft comment** below.
4. Pick a skill. For a package you haven't reviewed yet, choose **First review** (about a
   minute). The co-reviewer reads the package source at the commit the build machines built,
   the check logs and the issue thread, then writes a first review into your draft. Its
   headings and checkboxes follow the Bioconductor package guidelines and the points
   reviewers raise most often. Code is cited with links to the exact lines.
5. Read and edit. Change the draft yourself, or ask in the chat: "drop the style points",
   "check the license of the bundled data", "is this a near-duplicate of an existing
   package?", "make the tone warmer". Every change it makes is shown as a diff and can be
   undone.
6. Click **Copy markdown**, then **Comment on GitHub** and paste. A fixed last line
   says the draft was written with AI assistance and edited by you.

You decide what the submitter sees. The co-reviewer can only change your draft. You are
still responsible for applying the
[Bioconductor guidelines](https://contributions.bioconductor.org/) and checking each point
before you post.

### Skills

| Skill | Use when | Time |
|---|---|---|
| **First review** | You haven't reviewed the package yet and want a full first draft to edit. | ~1 min |
| **Follow-up** | The submitter replied or pushed a new version. Lists which of your points are resolved, partly resolved or still open. | 1–2 min |
| **Check triage** | Checks show errors, warnings or notes. Explains which must be fixed and whether the submitter's justifications hold. | 10–30 s |
| **Fit & overlap** | You're unsure the package belongs in Bioconductor (vs CRAN), or suspect it duplicates an existing package. | ~30 s |
| **License & provenance** | Before accepting any package, or when it bundles data, vendored code, or code adapted from elsewhere or written with AI. Checks the license, where third-party code and data come from, whether they can be redistributed, and AI disclosure. | 30–60 s |
| **Nudge** | The review has stalled. Writes a short, friendly status or reminder comment. | ~5 s |

You can also just ask questions: "where is the data in `inst/extdata` from?", "which exported
functions have no tests?", "what did the submitter change since my last comment?"

**Limits.** The co-reviewer reads code but doesn't run it. It can be wrong, so check before
you post. Your draft is saved in this browser only, so it won't follow you to another
computer.

## Reading the queue

**Whose move.** It is the *reviewer's move* when the reviewer hasn't commented since being
assigned, or when the submitter has commented or pushed a new version since the reviewer's
last comment. Otherwise it is the *submitter's move*.

**Two reviewers.** When a second reviewer is assigned, for example a core-team member who
takes over a stalled review, the move belongs to the submission, not to each person. A
comment by either reviewer counts for both, and the wait runs from the first assignment. The
review page still says which reviewer hasn't commented.

**Waiting** is the number of days since the move passed to whoever has it now:

| Band | Waiting | Meaning |
|---|---|---|
| fresh | up to 14 days | normal |
| due | 15–28 days | past the usual two-to-three-week turnaround |
| stale | 29–60 days | probably needs attention |
| stalled | over 60 days | candidate for reassignment |

**At risk** marks a submission where it is the reviewer's move, the next release deadline
is less than 30 days away, and the reviewer either hasn't commented yet or has waited more
than 14 days.

**Current checks** come from r-universe as it is now. r-universe re-runs checks without
posting to the issue, so they can be newer than the bot's last report. The page says when
the two differ.

Each review page has **Why N days?**, which lists the events behind the number.

## For the core team (Admin)

**Overview** lists every open submission. It shows headline numbers, a *Needs attention*
list (unassigned, stalled and at-risk submissions), the load on each reviewer, and a
filterable table of all submissions. **Co-review usage** shows how the co-reviewer is used
and what it costs.

## What the numbers can't see

"Whose move" and "no reviewer comment" count only comments by the assigned reviewer in the
issue thread. A review done by someone else, by email, or as a pull request on the package's
repository doesn't show up. Data is public GitHub and r-universe information, refreshed
every 5 minutes.

## Privacy

The app keeps a record of sign-ins (GitHub login and time) and of co-reviewer use (login,
issue, skill, model, tokens and cost, and actions such as copying a draft). It uses these
to understand use and to manage cost. Requests to the co-reviewer go through Cloudflare
AI Gateway, which logs them, including the text sent to the model. The app itself doesn't store
your draft or chat. Page views are counted with Google Analytics.

## Questions and feedback

Open an issue on [seandavi/bioc-contrib-intelligence](https://github.com/seandavi/bioc-contrib-intelligence/issues),
or contact Sean Davis.
