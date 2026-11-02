# Spec: Bioconductor reviewer app

Status: draft for design handoff · 2026-11-02 · data: `bcintel` corpus fetched 2026-11-02

This spec covers **what** the app shows and does, and which data backs each element.
Visual design, layout and interaction details are left to the design pass.

## 1. Problem

Submitters can't see where their review stands, reviewers have no personal queue, and
nobody has one place to spot and fix stalled reviews. A real email (2026-11-02,
BiocContributions #170, package *saintexpress*):

> Reviewer assigned 28 Aug, more than two months ago. No review comments since. Build OK
> on all platforms, one BiocCheck WARNING, justified on 21 Oct. The 3.24 manifest
> deadline is 18 Nov, about two weeks away. Could you reassign the review?

The submitter had to piece that together by hand. Our data already had it: reviewer's
move, 66 days, no reviewer comment since assignment.

How big the problem is (BiocContributions, open issues, 2026-11-02):

| Measure | Value |
|---|---:|
| Open submissions | 116 |
| Open reviewer assignments (issue × reviewer) | 120 across 17 reviewers |
| Reviewer's move for > 28 days | 48 |
| Assigned > 28 days ago, reviewer has not commented since | 41 |
| Reviewer's move for longer than the median assign→accept time (39 d) | 35 |
| Open, no reviewer assigned | 4 |
| Historical assign→accept, accepted packages (n = 75) | median 39 d, p90 92 d |

Caveat: "reviewer has not commented" counts only comments by the *assignee* in the
issue thread. Review work done by someone else, or outside the thread, isn't seen.
The UI must say so (see §6.4).

## 2. Users and roles

| Role | Who | Needs |
|---|---|---|
| **Reviewer** | GitHub user assigned to ≥ 1 issue on `Bioconductor/BiocContributions` (17 today; loads of 2–14 open) | "What do I owe, oldest first? What changed since I last looked?" Draft a review faster. |
| **Admin** | Core team (decision pending, §9.2) | See every queue at once; spot stalls, deadline risk and overloaded reviewers; assign, unassign and reassign. |
| *Submitter* (later) | Package author | Read-only status of their own submission. Out of scope for v1, but nothing should rule it out. |

Sign-in is **GitHub OAuth**. Role comes from GitHub: a reviewer is anyone with
assignments in the data; the admin view needs a permission check (§9.2). Write actions
use the signed-in user's own GitHub token, so GitHub enforces who may do what and
every action shows up under that person's name on the issue.

## 3. Core concept: whose move is it?

Every open assignment is in exactly one of these states:

- **Reviewer's move**: the reviewer hasn't commented since assignment, *or* the
  submitter has commented or pushed a new version since the reviewer's last comment.
- **Submitter's move**: the reviewer commented last and the submitter hasn't
  responded.

**Waiting** = days since the move passed to the current party. This is the main
number in the app. Proposed severity bands (configurable, based on the historical
distribution):

| Band | Waiting (reviewer's move) | Meaning |
|---|---|---|
| fresh | ≤ 14 d | normal |
| due | 15–28 d | past the documented 2–3 week reviewer norm |
| stale | 29–60 d | intervention likely needed |
| stalled | > 60 d | candidate for reassignment |

The same bands apply on the submitter's side; the legacy tracker auto-closed inactive
submissions after about 4 months.

**Deadline risk:** an assignment is *at risk* when it's the reviewer's move and the
next release deadline (e.g. 3.24 manifest, 18 Nov 2026) is closer than the typical
remaining review time. The deadline is an admin-set date; there's no feed for it.

## 4. Data available

Everything comes from public GitHub data on `Bioconductor/BiocContributions` (issues +
full per-issue timeline), refreshed every 6 h. ✅ = in the current data, 🔧 =
derivable from data we already store, but not yet computed, ❌ = not available.

### 4.1 Per assignment (the queue row)

| Field | Status | Example |
|---|---|---|
| issue number, package name (title), submitter login | ✅ | 170, saintexpress, `submitter-1` |
| reviewer login | ✅ | `reviewer-a` |
| assigned_at | ✅ | 2026-08-28 |
| reviewer_last (reviewer's last comment) | ✅ | null = never |
| reviewer_turn (bool), waiting_since | ✅ | true, 2026-08-28 |
| comments_since / pushes_since (submitter activity since reviewer's last comment) | ✅ | 1 comment, 1 push |
| stage label + stage_since | ✅ | `review in progress` since 2026-08-28 |
| last comment (author + first 300 chars) | ✅ | |
| build labels | ✅ but cumulative: labels pile up (`Build OK`, `Build Warning` both present) and don't show the *current* result | |
| **latest per-platform check result** | 🔧 parse the bot's newest "build detected" comment: version, per-platform table (source, bioc-checks, linux, macos, windows) × OK/NOTE/WARNING/ERROR, links to runs and the r-universe check page | 0.99.0: bioc-checks WARNING, others OK |
| package version history (each push) | 🔧 same bot comments | one entry per pushed version |
| comment signals per human comment (Clef pass, already run once over all 801 tracker comments) | 🔧 needs a scheduled re-run: `asks_question`, `hands_off`, `blocked`, `pushback`, `delay_notice`, `urgency`, `review_kind` (full / partial / follow_up / nudge / administrative) | "submitter asked a question 12 d ago, unanswered" |
| source repo URL, staging repo, r-universe page | 🔧 bot comments / issue body | |
| reviews done outside the issue thread (PR reviews on the package repo, email) | ❌ | |
| reviewer availability / out-of-office | ❌ except when stated in a comment (`delay_notice` signal) | |

### 4.2 Per issue (detail page)

The full timeline in order: human comments (markdown, with anchors to the GitHub
comment), bot comments (collapsible), and events (labeled, unlabeled, assigned,
unassigned, closed, reopened) with actor and timestamp. ✅

### 4.3 Per reviewer (aggregates)

Open count, reviewer's-move count, oldest and median wait. ✅ Historical throughput
(accepted per quarter, median assign→first-comment, median assign→accept) 🔧 from
closed issues (139 on the new tracker, ~4,300 on the legacy tracker).

### 4.4 Slash commands in use (new tracker)

`/accept-policies` (230), `/confirm-decline-package` (6), `/recheck` (2). Comments that
are only slash commands are excluded from "activity".

## 5. Screens

### 5.1 Sign-in

GitHub sign-in button and a one-line description of the app. After sign-in: reviewers
go to **My queue**, admins to **Overview** (with My queue in the navigation).

### 5.2 My queue (reviewer home)

- Summary strip: open assignments, my move, oldest wait, number at deadline risk.
- Queue table, my move first, then by waiting desc. Columns: package (#, name),
  submitter, **waiting (with band)**, what changed since my last comment ("2 comments,
  1 push"), current check status (per-platform chips), stage, last comment snippet,
  AI review status (§7).
- A section for submitter's-move items, collapsed by default.
- Row → Review detail.
- Empty state: "Nothing assigned to you."

### 5.3 Review detail (per issue)

- Header: package, issue link (opens GitHub), submitter, reviewer(s), stage, whose move
  + waiting band, deadline risk flag.
- **Status panel:** latest check result per platform with links; version history;
  "since your last comment" summary; unanswered questions from the submitter (comment
  signal).
- **Timeline:** the conversation, with reviewer/submitter/core/bot visually distinct;
  bot comments and label events collapsed; each entry links to its GitHub anchor.
- **AI review panel** (§7).
- Admin-only: the assignment controls from §6.3, inline.

### 5.4 Overview (admin home)

- Headline numbers: open submissions, unassigned, stalled, at deadline risk, median
  wait.
- **Needs attention** list (main element): unassigned issues, stalled assignments,
  at-risk assignments, submitter questions unanswered > N days. Each row has a direct
  action (assign / reassign / open).
- **Reviewer load** table: reviewer, open, their move, oldest wait, median wait,
  historical median time-to-first-comment. Sortable. Row → that reviewer's queue
  (same view as 5.2, read-only for the admin).
- **All submissions** table: every open issue, filterable by stage, band, reviewer,
  check status, at-risk.
- Data freshness ("updated 2 h ago") visible on every page.

### 5.5 Assign / reassign dialog (admin)

Opened from Overview, the Needs-attention list, or Review detail.

- Current reviewer(s) and how long they've had it.
- Candidate list: every known reviewer, with current load (open / their move / oldest
  wait). Topic match (biocViews overlap with past reviews) 🔧, as a later addition.
- Actions: **assign**, **unassign**, **reassign** (unassign + assign in one step).
- Optional comment posted to the issue (prefilled, editable), e.g. "Reassigning to
  @x to keep this on track for 3.24. Thanks @y."
- Confirmation shows exactly what will happen on GitHub before it's sent.

## 6. Actions and behaviour

### 6.1 Read

Every page works from the 6-hourly data snapshot. No GitHub calls needed to browse.

### 6.2 Write actions (all use the signed-in user's GitHub token)

| Action | Who | GitHub effect |
|---|---|---|
| Post comment | reviewer (own issues), admin | issue comment as the user |
| Assign / unassign / reassign | admin | issue assignees change, plus optional comment |
| Request AI review | reviewer (own issues), admin | none; runs the review service (§7) |

After a write, the affected row updates right away (optimistic), shows "pending
sync" until the next data refresh confirms it, and shows GitHub's error message if
the call fails (e.g. not enough permission).

### 6.3 Reassignment rule of thumb (shown as guidance, not automated)

Suggest reassignment when an item is *stalled* or *at deadline risk* **and** the
reviewer hasn't commented since assignment. The app never reassigns on its own.

### 6.4 Honesty about the data

A permanent, short note: "Whose move" is computed from the issue thread only. Reviews
done elsewhere aren't visible. Every computed number links or expands to the events
it came from (e.g. "waiting 66 d → assigned 2026-08-28, no reviewer comment since").

## 7. AI review

### 7.1 Behaviour

- On Review detail, a **Run AI review** button (reviewer of that issue, or admin).
  Sign-in is required, which keeps the cost per request accountable.
- Runs a fixed set of **review axes** quickly and in parallel. Each axis returns
  a verdict (`ok` / `concern` / `blocker`), a one-line summary, and markdown details with
  file/line citations where relevant.
- Proposed axes (final list pending §9.1):
  1. **Code**: structure, reuse of core Bioconductor classes vs reinventing them,
     error handling, tests.
  2. **Documentation**: vignette quality and runnable examples, man-page coverage.
  3. **Bioconductor vs CRAN fit**: does it use or extend Bioconductor infrastructure,
     or would it belong on CRAN?
  4. **Overlap with existing Bioconductor packages**: closest existing packages, with
     links, and how this one differs.
  5. (optional) **Check triage**: plain-language explanation of the current
     BiocCheck / R CMD check NOTE/WARNING/ERROR lines, and whether the submitter's
     justification addresses them. *Explains* what the tools reported; never
     re-derives or softens it.
- Results show as **axis chips** (verdict colour + label) on My queue rows, Overview rows
  and the Review detail header, so the state is visible without opening anything.
- A results view (separate window or large panel) shows the combined markdown
  review, one section per axis, in an **editor**, with two actions:
  - **Post to issue**: posts the edited text as a comment from the reviewer
    (confirmation step, shows the target issue).
  - **Copy markdown**: for pasting into the reviewer's own comment.
- The review is tied to the package version it ran on (e.g. 0.99.3). When a newer
  version is pushed, chips show as *outdated* and offer a re-run.

### 7.2 States to design

not run · running (per axis progress) · done · partly failed (some axes errored) ·
outdated (new version since) · posted (link to the resulting comment).

### 7.3 Rules

- Advisory only. Nothing is posted without an explicit click after editing is possible.
- Posted text is marked as AI-assisted (a short footer the reviewer can't edit out, or
  a visible label; decide in design).
- Only the reviewer of the issue and admins can see AI results; they aren't shown to
  submitters.

## 8. Non-goals (v1)

- Submitter-facing view (planned later).
- Automatic reassignment, nudges, or any bot posting on its own.
- Label changes or accept/decline decisions (the existing bot and core team own these).
- The legacy `Bioconductor/Contributions` tracker (history and calibration only).
- Notifications (email / Slack). Possible later.

## 9. Open decisions

1. **AI review engine.** Package-content review was put on hold in this repo
   (2026-10-16) in favour of Levi Waldron's BiocPkgReviewer. Options: call
   BiocPkgReviewer; reopen our Clef-based axes (Gate 1 fit/redundancy experiments are
   parked, not abandoned); or ship v1 without it. The UI in §7 works the same
   whichever engine is chosen.
2. **Who is an admin.** GitHub permission on BiocContributions (whoever GitHub
   allows to assign), or an explicit core-team list.
3. **Visibility.** Logged-in only, or a public read-only overview. Per-reviewer
   overdue numbers are sensitive for volunteer reviewers; current lean is
   logged-in only.
4. **Deadline source.** Admin-entered dates vs reading the Bioconductor release
   schedule.

## 10. Sample data for design

Shape of the current snapshot (`data.json`), one row per open assignment. Logins are
pseudonymised; numbers and labels are real.

```json
{
  "generated_at": "2026-11-02T13:18:27Z",
  "queue": [
    {"issue_number": 170, "title": "saintexpress", "submitter": "submitter-1",
     "reviewer": "reviewer-a", "reviewer_turn": true,
     "assigned_at": "2026-08-28T01:44:27Z", "waiting_since": "2026-08-28T01:44:27Z",
     "reviewer_last": null, "comments_since": 1, "pushes_since": 1,
     "build": ["Build OK", "Build Warning"], "stage": "review in progress",
     "last_comment": "submitter-1: Thank you @reviewer-a for taking on the review. Below is our justification for the BiocCheck WARNING and the two NOTEs of the 0.99.0 build. ..."},
    {"issue_number": 27, "title": "GO.ddb, semantic SQL for Gene Ontology",
     "submitter": "submitter-2", "reviewer": "reviewer-b", "reviewer_turn": true,
     "assigned_at": "2026-05-12T17:26:02Z", "waiting_since": "2026-05-12T17:26:02Z",
     "reviewer_last": null, "comments_since": 1, "pushes_since": 5,
     "build": ["Build OK", "Build Warning", "Build Note"], "stage": "review in progress",
     "last_comment": "submitter-2: I did"}
  ],
  "unassigned": [
    {"issue_number": 46, "title": "epiwraps", "submitter": "submitter-3",
     "created_at": "2026-06-09T11:42:22Z",
     "labels": ["precheck-passed", "policies-accepted", "pre-review",
                "Build OK", "Build Error", "Build Note"]}
  ]
}
```

AI review body: one markdown file per open issue at `i/<n>.review.md`. Until the
review engine is chosen (§9.1), every file holds the placeholder `REVIEW BODY HERE`;
design the review panel and editor around arbitrary markdown.

Latest check result, as the bot posts it (to be parsed into a structured field):

```
✅ First build detected for saintexpress, version 0.99.0.
| Platform              | R     | Status     |
| source                | 4.6.1 | ✅ OK      |
| bioc-checks           | 4.6.1 | ⚠️ WARNING |
| linux-release-x86_64  | 4.6.1 | ✅ OK      |
| macos-release-arm64   | 4.6.1 | ✅ OK      |
```

Realistic ranges for layout: 17 reviewers; 2–14 open assignments each; waits from 0
to 174 days; package names up to ~45 characters; issue threads up to ~140 timeline entries (median 24).
