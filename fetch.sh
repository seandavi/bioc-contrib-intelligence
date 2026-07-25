#!/usr/bin/env bash
# Backfill Bioconductor submission-tracker data to JSONL (source of truth).
# Both the legacy tracker (Bioconductor/Contributions, ~4300 issues) and the
# new one (Bioconductor/BiocContributions). Full refetch each run.
# ponytail: full refetch, not incremental. ~50 paginated calls, well under the
# 5000/hr limit. Add a `since=<updated_at watermark>` filter if this gets slow.
set -euo pipefail

REPOS=("Bioconductor/Contributions" "Bioconductor/BiocContributions")
OUT="$(dirname "$0")/data"

fetch() {  # repo endpoint outfile  — paginate an array endpoint to JSONL, tagging _repo
  local repo="$1" ep="$2" out="$3"
  gh api --paginate "repos/$repo/$ep" \
    --jq ".[] | . + {_repo:\"$repo\"}" > "$out"
  echo "  $(wc -l < "$out") -> $out"
}

for repo in "${REPOS[@]}"; do
  slug="${repo##*/}"; slug="${slug,,}"
  dir="$OUT/$slug"; mkdir -p "$dir"
  echo "== $repo =="

  # Issues (state=all is essential; endpoint also returns PRs — drop them).
  gh api --paginate "repos/$repo/issues?state=all&per_page=100" \
    --jq ".[] | select(.pull_request|not) | . + {_repo:\"$repo\"}" \
    > "$dir/issues.jsonl"
  echo "  $(wc -l < "$dir/issues.jsonl") -> $dir/issues.jsonl"

  # Repo-wide streams — one pass each, no per-issue loop.
  fetch "$repo" "issues/comments?per_page=100" "$dir/comments.jsonl"
  fetch "$repo" "issues/events?per_page=100"   "$dir/events.jsonl"
done
echo "done."
