#!/usr/bin/env bash
# Reactive tick for cron: refresh the corpus, then review changed submissions and
# draft safe-fix PRs (all dry-run to bot_out/). Idempotent — unchanged
# submissions are skipped, so most runs are cheap. Self-contained env so it works
# under cron's minimal shell. Logs to bot_out/cron.log.
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"
REPO="/home/davsean/Documents/git/bioc-contrib-intelligence"
cd "$REPO"
mkdir -p bot_out
exec >> bot_out/cron.log 2>&1
echo "===== cycle $(date -u +%Y-%m-%dT%H:%M:%SZ) ====="
# Set BCINTEL_LIMIT=N to cap NEW reviews per run (per repo); unset = full coverage.
LIMIT_ARG=""
[ -n "${BCINTEL_LIMIT:-}" ] && LIMIT_ARG="--limit ${BCINTEL_LIMIT}"
uv run bcintel cycle --patch ${LIMIT_ARG}
echo "----- done $(date -u +%Y-%m-%dT%H:%M:%SZ) -----"
