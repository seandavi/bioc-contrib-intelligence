# comments ledger

Append-only. One line per run; details in runs/<run_id>/.

- 20261016T110026Z-calib-v1 · git 108fe5f+dirty · n=40 · $0.0251 · v1 questions, 40-comment calibration sample
- 20261016T110129Z-calib-v2-same · git 108fe5f+dirty · n=40 · $0.0245 · v2 questions on the v1 sample
- 20261016T110132Z-calib-v2-fresh · git 108fe5f+dirty · n=40 · $0.025 · v2 questions on a fresh 40
- correction: 20261016T110129Z-calib-v2-same is NOT the v1 sample (unordered query made seeded sampling non-reproducible; fixed with ORDER BY c.id). Treat it as another fresh 40; the true same-sample rerun follows.
- 20261016T110154Z-calib-v2-v1sample · git 108fe5f+dirty · n=40 · $0.0258 · v2 questions on the exact v1 comment ids
- 20261016T110301Z-smoke-v3 · git 108fe5f+dirty · n=12 · $0.0073 · v3: delay_notice on both sides, +urgency
