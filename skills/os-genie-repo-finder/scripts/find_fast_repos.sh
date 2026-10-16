#!/usr/bin/env bash
# Rank SIGNIFICANT repos by how fast they actually merge outside contributors.
# Usage: find_fast_repos.sh <language> [min_stars=3000] [limit=25]
# Output (TSV, fastest first): repo stars median_merge_hours ext_merged/60 recent closed PRs last_push
# "ext" = PR author association NONE/CONTRIBUTOR/FIRST_TIME*; bots excluded. Read-only.
set -euo pipefail
lang=$1; stars=${2:-3000}; limit=${3:-25}
gh search repos --language "$lang" --stars ">=$stars" --archived=false --sort updated \
  --limit "$limit" --json fullName,stargazersCount,pushedAt,license \
  --jq '.[]|select(.license!=null)|[.fullName,.stargazersCount,.pushedAt[:10]]|@tsv' |
while IFS=$'\t' read -r repo st push; do
  gh api "repos/$repo/pulls?state=closed&per_page=60&sort=updated&direction=desc" 2>/dev/null |
  jq -r --arg r "$repo" --arg s "$st" --arg p "$push" '
    map(select(.merged_at!=null and (.user.type!="Bot"))) as $all
    | ($all|map(select(.author_association|IN("NONE","CONTRIBUTOR","FIRST_TIME_CONTRIBUTOR","FIRST_TIMER")))) as $ext
    | ($ext|map((.merged_at|fromdateiso8601)-(.created_at|fromdateiso8601))|sort) as $d
    | if ($d|length)>=3 then [$r,$s,(($d[($d|length/2|floor)]/3600)|round),($ext|length),$p]|@tsv else empty end'
done | sort -t$'\t' -k3,3n
