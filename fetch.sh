#!/usr/bin/env bash
# Backfill Bioconductor submission-tracker data to JSONL (source of truth).
# Legacy tracker (Bioconductor/Contributions, ~4300 issues) + new one
# (Bioconductor/BiocContributions). Resumable: re-run to continue/refresh.
#
# We fetch the per-issue TIMELINE, not the repo-wide comments/events streams,
# because those are hard-capped by GitHub at 30k items (page 300 -> HTTP 422)
# and the legacy repo has more than that. The timeline gives comments AND
# label/assign/close/cross-reference events in one call per issue.
# ~4400 issues -> ~4400 calls, within the 5000/hr authenticated limit.
# ponytail: full-issue refetch of timelines each run for issues not yet stored;
# add an `updated_at` watermark to refresh only changed issues if this gets slow.
set -euo pipefail

REPOS=("Bioconductor/Contributions" "Bioconductor/BiocContributions")
OUT="$(dirname "$0")/data"

for repo in "${REPOS[@]}"; do
  slug="${repo##*/}"; slug="${slug,,}"
  dir="$OUT/$slug"; mkdir -p "$dir"
  echo "== $repo =="

  # Issues (state=all is essential; endpoint also returns PRs — drop them).
  gh api --paginate "repos/$repo/issues?state=all&per_page=100" \
    --jq ".[] | select(.pull_request|not) | . + {_repo:\"$repo\"}" \
    > "$dir/issues.jsonl"
  echo "  issues: $(wc -l < "$dir/issues.jsonl")"

  # Per-issue timeline, resumable — skip issues already captured.
  tl="$dir/timeline.jsonl"; [ -f "$tl" ] || : > "$tl"
  declare -A done=()
  while read -r n; do done["$n"]=1; done < <(jq -r '._issue' "$tl" 2>/dev/null | sort -u)
  new=0
  while read -r num; do
    [ -n "${done[$num]:-}" ] && continue
    gh api --paginate "repos/$repo/issues/$num/timeline?per_page=100" \
      -H "Accept: application/vnd.github.mockingbird-preview+json" \
      --jq ".[] | . + {_repo:\"$repo\", _issue:$num}" >> "$tl"
    new=$((new+1))
  done < <(jq -r '.number' "$dir/issues.jsonl")
  unset done
  echo "  timeline: +$new issues, $(wc -l < "$tl") events total"
done
echo "done."
