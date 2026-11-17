# Review corpus distillation (#34)

Turns past Bioconductor package reviews into material for the co-review skills (#33, #39).

```bash
uv run python experiments/reviews/distil.py all --data ../bioc-contrib-intelligence/data
```

Per-stage caches live in `<data>/review-corpus/` (gitignored), so reruns only pay for what's missing.

## Corpus

Comments by an issue assignee, not a bot, not the submitter, longer than 1,500 characters, on
both trackers: 2,433 comments on 1,657 submissions (120 new tracker, 2,313 legacy) by 29
reviewers. Haiku classified 1,408 of them as first full reviews (101 new, 1,307 legacy).

## Method

| Stage | Model | What |
|---|---|---|
| extract | Haiku 5.5 | one call per comment: review kind, findings `{category, point, quote}`, structure, tone |
| cluster | Sonnet 5.5 | one call per category: canonical checklist items from the extracted points |
| assign | Haiku 5.5 | batches of 80 points → which checklist item each is an instance of |
| report | Sonnet 5.5 | structure narrative; counts, shares and quotes are computed, not generated |

Outputs: `out/checklist.md` (16 categories, items ranked by how many reviews raise them, share of
first reviews overall / new / legacy, verbatim typical wording), `out/structure.md` (how first
reviews and follow-ups are laid out, section names, checkbox use, tone), `out/examples.md` (three
submissions, first review + follow-ups, logins replaced by role labels).

Examples were picked from candidates (same reviewer wrote a first review and a follow-up, many
categories, different reviewers, moderate length): BiocContributions #56 and #75, Contributions #762.

## Caveats

- Categories, items and assignments are model judgements; spot-check before quoting numbers.
- New-tracker shares rest on 101 first reviews: treat differences under ~10 points as noise.
- Only long comments: short follow-ups and reviews done outside the thread are missing.
- 12 comments failed extraction in the first pass and succeeded on the rerun.
- The first `assign` attempt failed on 88 % of batches: Haiku returned empty text at
  `max_tokens=2000` (hidden reasoning used the budget). Raised to 8,000; the rerun had 0 errors.
  That failed attempt's cost is included below; its wall time wasn't logged (about 4 min).

## Cost and time

Measured 2026-11-14 on onclappc02 through AI Gateway (`default`, metadata `job=review-corpus`),
8 concurrent requests. Cost is the gateway's own per-request cost, summed by `distil.py cost`.

| Model | Calls | Tokens in | Tokens out | Cost |
|---|---:|---:|---:|---:|
| claude-haiku-5.5 | 3,077 | 8,515,599 | 5,016,063 | $3.36 |
| claude-sonnet-5.5 | 18 | 456,228 | 34,028 | $1.25 |
| **Total** | 3,095 | 8,971,827 | 5,050,091 | **$4.61** |

Wall time: stages logged in `runs.jsonl` sum to 2,330 s (38.8 min): extract 1,627 s over four
resumed passes, cluster 216 s, assign 442 s, report 45 s (two runs). Elapsed from first call to
last: 11:20:34–12:10:44 UTC, 50.2 min, including the failed assign attempt and a restart.
