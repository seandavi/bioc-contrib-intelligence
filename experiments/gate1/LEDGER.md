# Gate 1 eval ledger

Append-only. One line per run; details in runs/<run_id>/.

- 20261016T094927Z-dev-clef · git 0193b76+dirty · n=64 (40+/24-) · best AUC bioc_fit=0.779 · baseline=0.721 · $0.0155 · v1 questions
- 20261016T095032Z-dev-clef · git 0193b76+dirty · n=62 (40+/22-) · best AUC bioc_fit=0.808 · baseline=0.734 · $0.0167 · v2: +interop_gap, drop inactivity-declined
- 20261016T100150Z-test-clef · git cc1bad4 · n=1595 (1513+/82-) · best AUC uses_bioc_classes=0.695 · baseline=0.677 · $0.4408 · v2 frozen; full test split, natural class ratio
- 20261016 coverage check (not a model run) · source-as-submitted availability on GitHub for all 104 eval negatives + 120 sampled accepted (coverage/20261016-source-availability.jsonl) · retrievable: declined 44/63 (70%), needs-interop 35/41 (85%), accepted 111/120 (92%); 72/224 have the bot's built sha, the rest use the last commit before the issue opened · scip-r static index smoke-tested on #2508 (needs interop) and #975 (accepted)
