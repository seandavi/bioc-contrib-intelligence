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
# Live tracker every tick; the legacy tracker (history) only in the first tick after 00:00 UTC.
# ponytail: a missed midnight tick skips legacy for a day; harmless for a frozen tracker.
REPOS=(--repo Bioconductor/BiocContributions)
[ "$(date -u +%H%M)" \< "0005" ] && REPOS=()
uv run bcintel cycle "${REPOS[@]}"
echo "----- done $(date -u +%Y-%m-%dT%H:%M:%SZ) -----"
