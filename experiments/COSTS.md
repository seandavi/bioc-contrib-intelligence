# Cost and time log

Every model run and pipeline step, with what it cost and how long it took, so the
work can be written up. Model pricing: Cloudflare Clef, $0.24 per million input
tokens and no output charge (developers.cloudflare.com/workers-ai/models/clef,
read 2026-10-16). Costs are computed from the token counts the API returned.

From commit `c3c63b4`+1 onward, every run records `started_at`, `finished_at` and
`wall_seconds` in its `config.json`. Earlier runs are backfilled below, and the
**How measured** column says where each number came from:

- `config`: from the run's own config.json.
- `time`: shell `time` output captured during the session.
- `files`: file creation or modification timestamps (start = first output file,
  end = final write). Accurate to within seconds.
- `run_id`: the run id is the finish timestamp; the start is taken from the previous
  event (commit time or previous run end).
- `n/a`: not recorded and not recoverable; all of these are runs that were
  noticeably under a minute.

All runs were on 2026-10-16 from onclappc02. Clef calls went through Workers AI with
8 (calibration and gate runs) or 16 (full comment passes) concurrent requests.

## Comment signals (`experiments/comments/`)

| Run | Items | Input tokens | Tokens/item | Cost | Wall time | How measured |
|---|---|---|---|---|---|---|
| calib-v1 | 40 comments | 104,691 | 2,617 | $0.025 | < 1 min | n/a |
| calib-v2-same (actually a second fresh 40; see LEDGER) | 40 | 101,967 | 2,549 | $0.024 | < 1 min | n/a |
| calib-v2-fresh | 40 | 104,109 | 2,603 | $0.025 | < 1 min | n/a |
| calib-v2-v1sample | 40 | 107,496 | 2,687 | $0.026 | < 1 min | n/a |
| smoke-v3 | 12 | 30,452 | 2,538 | $0.007 | < 1 min | n/a |
| **full, BiocContributions** | 801 | 2,043,693 | 2,551 | **$0.49** | ~26 s | files + run_id (labels.jsonl created 11:03:16Z, run finished 11:03:42Z) |
| **full, Contributions (legacy)** | 31,892 | 86,069,934 | 2,699 | **$20.66** | **17 min 17 s** (~31 comments/s) | run_id (11:03:42Z to 11:20:59Z, labels.jsonl last write 11:20:59Z) |

Calibration total: 172 comments, $0.11. Human checking: 40 comments read in full
against all answers (v1), the same 40 compared after rewording (v2), and a fresh 40
reviewed in a compact view (v2-fresh).

Questions per comment: 14 for submitter comments and 24 for reviewer or core-team
comments, all in one call each. Error rate in the full passes: 0 of 32,693.

## Gate 1 experiments (`experiments/gate1/`, parked)

| Run | Items | Input tokens | Cost | Wall time | How measured |
|---|---|---|---|---|---|
| dev v1 | 64 DESCRIPTIONs | 64,579 | $0.016 | < 1 min | n/a |
| dev v2 | 62 | 69,755 | $0.017 | < 1 min | n/a |
| test v2 | 1,595 | 1,836,638 | $0.44 | 1 min 14 s | time |
| source-availability check | 224 repos (~450 GitHub API calls) | none | $0 | < 1 min | n/a |
| v3 source fetch | 1,052 tarballs (913 ok, 584 MB kept) | none | $0 | ~1 min 44 s | files (first src dir 10:12:19Z, manifest written 10:14:03Z) |
| v3 scip-r index | 913 packages (index + Parquet export) | none | $0 | 6 min 52 s (8 parallel jobs) | time |
| v3 features | 871 packages | none | $0 | seconds | files |

## Reference point

Bioconductor/BiocPkgReviewer (Levi Waldron): mean **$7.67 per package review**
($130.41 over 17 runs). That figure is list-price accounting of headless `claude -p`
sessions (7 Opus passes per package), computed from `cost_usd` in each run's
`findings.json`. Pollers actually run on their own subscriptions, so it is notional.
Source: our survey of its `results` branch, 2026-10-16.

For scale, labelling the whole legacy tracker's human conversation (31,892 comments)
cost about the same as 2.7 BiocPkgReviewer package reviews. The two tasks are not
comparable in kind: one is a reading of each comment, the other a review of a whole
package.
