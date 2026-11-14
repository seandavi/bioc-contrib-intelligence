# Cost and time log

Every model run and pipeline step, with what it cost and how long it took, so the work can be
written up. (The comment-signal and gate runs are logged in this file on branch
`comment-signals`; merging the two will need an add/add resolution.)

## Review corpus distillation (`experiments/reviews/`, #34)

2026-11-14, onclappc02, AI Gateway unified billing; cost = gateway-reported per-request cost.
Details in `experiments/reviews/LEDGER.md`.

| Run | Model | Calls | Tokens in / out | Cost | Wall time | How measured |
|---|---|---:|---|---:|---|---|
| extract (2,445 comments, 4 passes) | Haiku 5.5 | — | — | — | 1,627 s | config (`runs.jsonl`) |
| cluster (16 categories) | Sonnet 5.5 | — | — | — | 216 s | config |
| assign (326 batches; plus 1 failed attempt) | Haiku 5.5 | — | — | — | 442 s (+~4 min failed) | config; failed attempt from log timestamps |
| report (2 runs) | Sonnet 5.5 | — | — | — | 45 s | config |
| **Total** | Haiku | 3,077 | 8.52 M / 5.02 M | $3.36 | | gateway logs |
| | Sonnet | 18 | 0.46 M / 0.03 M | $1.25 | | gateway logs |
| | **all** | 3,095 | | **$4.61** | 50.2 min elapsed | |

Per-stage cost isn't split out: the gateway logs carry only `job`, not the stage.
