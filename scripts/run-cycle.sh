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
DAILY=""
[ "$(date -u +%H%M)" \< "0005" ] && REPOS=() && DAILY=1
uv run bcintel cycle "${REPOS[@]}"
# Publish the snapshot the reviewer app reads (R2 bucket data-bioc-reviews, made in
# seandavi/monode); --checksum uploads only changed files. Daily: back up the raw
# corpus too. Uses the `r2` rclone remote.
rclone sync site r2:data-bioc-reviews/snapshot --checksum --fast-list \
  --include "data.json" --include "i/**"
[ -n "$DAILY" ] && rclone copy data r2:data-bioc-reviews/raw --checksum --fast-list \
  --include "bioccontributions/**" --include "contributions/**" --include "comments/**"
echo "----- done $(date -u +%Y-%m-%dT%H:%M:%SZ) -----"
