#!/usr/bin/env bash
# Tick for cron/systemd: refresh the corpus, then rebuild the dashboard. Package
# review is no longer run here (see `bcintel review`). Self-contained env so it
# works under cron's minimal shell. Logs to bot_out/cron.log.
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"
REPO="/home/davsean/Documents/git/bioc-contrib-intelligence"
cd "$REPO"
mkdir -p bot_out
exec >> bot_out/cron.log 2>&1
echo "===== cycle $(date -u +%Y-%m-%dT%H:%M:%SZ) ====="
uv run bcintel cycle
echo "----- done $(date -u +%Y-%m-%dT%H:%M:%SZ) -----"
