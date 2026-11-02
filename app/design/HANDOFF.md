# Reviewer app: design handoff

Design comps for the Bioconductor reviewer app (spec: "Bioconductor reviewer app", draft 2026-11-02).
Live canvas: https://claude.ai/code/artifact/cd705780-da75-44dc-bfc4-73fb59ddc2e9 (private until shared).

The comps are a visual spec, not code to ship. Rebuild them in the app's own stack; copy the
values in `tokens.css` and the mappings below exactly.

## What's in this folder

| File | Screen | Spec |
|---|---|---|
| `screens/SignIn.dc.html` | Sign-in | §5.1 |
| `screens/Main.dc.html` | My queue (reviewer home) | §5.2 |
| `screens/ReviewDetail.dc.html` | Review detail, #170 saintexpress, reviewer's view + admin-only Assignment panel | §5.3, §6.3, §6.4 |
| `screens/Overview.dc.html` | Overview (admin home) | §5.4 |
| `screens/AssignDialog.dc.html` | Assign / unassign / reassign dialog | §5.5 |
| `screens/AssignConfirm.dc.html` | Confirm step + after-send states (pending sync, GitHub error) | §5.5, §6.2 |
| `screens/AIReview.dc.html` | AI review results editor | §7.1, §7.3 |
| `screens/AIStates.dc.html` | AI panel in all six states, table chips, key, post confirmation | §7.2 |
| `screens/canvas.json` | Canvas layout (frame sizes) | — |
| `tokens.css` | Colours, type, radii as CSS custom properties | — |

### Reading a `.dc.html` file

- Markup inside `<x-dc>` is the template. Inline `style="…"` is the visual spec.
- `{{ path }}` is a value from `renderVals()` in the `<script type="text/x-dc">` block at the bottom.
- `<sc-for list="{{ rows }}" as="r">` repeats; `<sc-if value="{{ flag }}">` branches.
- `renderVals()` holds the **sample data** and the style lookup maps (`S` checks, `B` bands, `V` verdicts).
  Port those maps to components; don't port the sample rows.
- The files need the design tool's runtime (`support.js`, not included), so they won't render if opened
  directly. View them on the canvas.

## Visual system

- **Type:** IBM Plex Sans (UI) and IBM Plex Mono (identifiers and numbers: package names, logins,
  issue numbers, versions, day counts). Base 13px / 1.45. Small text 12px. Page title 22px/600.
  Section titles 14–15px/600. Summary numbers 26px Mono/500.
- **Colour is only for meaning:** wait bands, check results, AI verdicts, risk. Everything else is neutral.
  One blue (`--accent`) for primary actions and links.
- **Layout:** content max-width 1392px, 24px page padding. Cards 8px radius, 1px `--border`.
  Wide tables sit in a horizontal-scroll box (min-width ~1280px); side rails wrap below the main column
  on narrow screens (flex-wrap, no fixed sidebars).
- **Targets:** buttons 34–40px tall on desktop; keep 44px on touch.

## Semantic mappings (implement exactly)

### Wait bands (§3)

| Band | Waiting | Chip bg / text / border |
|---|---|---|
| fresh | ≤ 14 d | `#EEF0F3` / `#3B4250` / `#D3D7DD` |
| due | 15–28 d | `#F8E3A8` / `#5C3F00` / `#E3C574` |
| stale | 29–60 d | `#F0A76A` / `#3D1A00` / `#DB8F4E` |
| stalled | > 60 d | `#7E2A10` / `#FFFFFF` / `#7E2A10` |

The ramp gets darker as it gets worse, so bands differ in lightness, not only hue. The chip always
shows the word too ("66 d stalled"). The same bands apply on the submitter's side.

```js
const band = d => d <= 14 ? 'fresh' : d <= 28 ? 'due' : d <= 60 ? 'stale' : 'stalled';
```

### Check results (latest bot report, per platform)

Platforms in order: `src` source, `bioc` bioc-checks, `lin` linux-release-x86_64, `mac` macos-release-arm64,
`win` windows. Chip = platform abbreviation + glyph; full name and status go in `title`/`aria-label`.

| Status | Glyph | bg / text / border |
|---|---|---|
| OK | ✓ (svg check) | `#FFFFFF` / `#1E5E35` / `#A9C9B3` |
| NOTE | N | `#DCE7FA` / `#1D4E99` / `#B5CBF0` |
| WARNING | W | `#F2C46D` / `#3F2600` / `#D9A84A` |
| ERROR | E | `#B42318` / `#FFFFFF` / `#B42318` |
| not reported | – | `#FFFFFF` / `#5F6673` / dashed `#B9BEC7` |

Never derive these from issue labels: labels pile up and don't show the current result.

### AI review axis chips

Letters: **C** Code, **D** Documentation, **F** Bioconductor vs CRAN fit, **O** Overlap, **T** Check triage.
22px squares, Mono 11px/600.

| State | Style |
|---|---|
| ok | same as check OK |
| concern | same as check WARNING |
| blocker | same as check ERROR |
| running | `#FFFFFF` / `#1D5BB8` / dashed `#1D5BB8` |
| not run / queued | `#FFFFFF` / `#5F6673` / dashed `#B9BEC7` |
| failed | `#FFFFFF` / `#B42318` / dashed `#B42318` |
| outdated (newer version pushed) | `#EEF0F3` / `#5F6673` / `#D3D7DD`, caption "Outdated · ran on x.y.z" in `#9A2E12` |

### Other tags

| Tag | Style |
|---|---|
| Your move / Reviewer | solid `#15181D`, white text |
| Submitter's move | outline `#B9BEC7`, text `#2B3038` |
| Unassigned | `#EFEAF8` / `#4E3585` / `#CDBFE6` |
| At risk for 3.24 | outline + text `#9A2E12`, warning-triangle icon |
| Pending sync | dashed `#1D5BB8`, text `#1D4E99`, clock icon |
| Admins only | `#EFEAF8` / `#4E3585` |

Timeline roles: reviewer blue `#1D5BB8`, submitter orange `#B85C1D` (comment header `#FBF1E9`,
border `#E9C9B0`), core purple `#6B4FA8`, bot/events grey `#8A919C`, collapsed by default.

## UI element → data (spec §4)

| UI | Source |
|---|---|
| Waiting chip | now − `waiting_since`; band from table above |
| Explanation under the chip ("Assigned 28 Aug, no comment from you since") | `assigned_at`, `reviewer_last` |
| Whose move | `reviewer_turn` |
| "Since your last comment" | `comments_since`, `pushes_since` |
| Checks chips + version | newest bot "build detected" comment (🔧 parser) |
| Stage + "since …" | `stage`, `stage_since` |
| Last comment (2-line clamp) | `last_comment` |
| At risk | `reviewer_turn` and (deadline − now) < typical remaining review time; deadline is admin-set |
| AI chips | AI review service result, tied to package version |
| Unassigned group | `unassigned[]` |
| Submitter question unanswered | comment signal `asks_question` (🔧 scheduled re-run) |
| Reviewer load | per-reviewer aggregates (§4.3); "Hist. to 1st comment" is 🔧 |
| Versions list | bot comments (🔧) |
| Data freshness ("Data as of … · 1 h ago") | `generated_at` |

## Behaviour shown in the comps

- My queue: your move first, longest wait first; submitter's-move section collapsed by default
  (`showSubmitterMove` toggle in `Main.dc.html` shows it expanded).
- Every computed number expands to the events behind it ("Why 66 days?" on Review detail).
- Writes are optimistic: the row updates at once and shows **Pending sync** until the next refresh confirms it.
  On failure, show GitHub's message verbatim and say what was and wasn't changed.
- Reassign = remove current assignee, add new one, optional prefilled comment, then a confirm step that
  lists exactly what will be sent to GitHub, in order.
- AI review results: editable markdown, plus a locked footer ("Drafted with AI assistance … edited by @user")
  added to every post. Post needs a confirm step naming the target issue.
- Permanent note on queue pages: "Whose move" comes from the issue thread only.

## Sample data: what's real

Real (snapshot 2026-11-02): 116 open, 4 unassigned, 120 assignments across 17 reviewers, 48 on the reviewer's
move > 28 d, 41 with no reviewer comment since assignment, and rows #170 saintexpress, #27 GO.ddb, #46 epiwraps
(dates, waits, reviewers, labels; check chips only for #170).

Placeholder: `package-d`… rows and issue numbers #8xx/#9xx, at-risk count 29, median wait, reviewer load numbers,
other check results, timeline wording beyond the opening of the 21 Oct comment, all AI review text.
Logins are pseudonyms (`reviewer-a`, `submitter-1`, `core-1`). App name "Bioconductor Reviews" is a placeholder.

## Not designed yet

- Empty state for My queue ("Nothing assigned to you.").
- Phone-width layouts (pages are fluid but no phone frames were drawn).
- Loading and data-fetch error states; sort and filter interactions beyond the static controls.
