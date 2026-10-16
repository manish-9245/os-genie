#!/usr/bin/env bash
# Pre-screen one issue BEFORE any agent spends time on it.
# Usage: prescreen.sh <owner/repo> <issue-number>
# Prints one JSON line: {issue, verdict, reasons[], approval[], last_maintainer_comment_days}
# verdict: PASS | REJECT. Needs gh (authed) + jq. Read-only: never posts anything.
set -euo pipefail
repo=$1; n=$2
now=$(date -u +%s)

iss=$(gh issue view "$n" --repo "$repo" --json state,assignees,labels,comments,updatedAt,title)
reasons=(); approval=()

[ "$(jq -r .state <<<"$iss")" = OPEN ] || reasons+=("not open")
[ "$(jq '.assignees|length' <<<"$iss")" -eq 0 ] || reasons+=("assigned")

# open PRs that cross-reference the issue (timeline) or mention it (search)
xref=$(gh api "repos/$repo/issues/$n/timeline" --paginate \
  --jq '[.[]|select(.event=="cross-referenced" and .source.issue.pull_request!=null and .source.issue.state=="open")]|length' | paste -sd+ - | bc)
hits=$(gh api -X GET search/issues -f q="repo:$repo is:pr is:open $n in:title,body" --jq .total_count)
[ "${xref:-0}" -eq 0 ] && [ "${hits:-0}" -eq 0 ] || reasons+=("open PR exists (xref=$xref, search=$hits)")

# recent non-maintainer claimants (45d) and maintainer doubt / approval
claim_re='(i.?ll take|i can take|work on (this|it)|assign (this|me|it)|can i (take|work|try)|i.?d like to (work|take|fix)|i.?m working|claim)'
doubt_re="(not sure (we|if)|don.?t know if|do we want|not convinced|probably not|wontfix|won.?t fix|lint rule|prefer not|reluctant|not a priority|closed, not accepted)"
okay_re='(pr welcome|happy to (review|accept)|go ahead|please (send|open|submit)|sounds good|feel free to (open|submit|send)|contributions? welcome|confirmed)'

claimants=$(jq --argjson now "$now" --arg re "$claim_re" '[.comments[]
  | select(.authorAssociation as $a | ["OWNER","MEMBER","COLLABORATOR"]|index($a)|not)
  | select((.createdAt|fromdateiso8601) > $now-45*86400)
  | select(.body|test($re;"i"))]|length' <<<"$iss")
[ "$claimants" -eq 0 ] || reasons+=("$claimants recent claimant comment(s) <45d")

maint=$(jq '[.comments[]|select(.authorAssociation as $a|["OWNER","MEMBER","COLLABORATOR"]|index($a))]' <<<"$iss")
jq -e --arg re "$doubt_re" 'any(.[];.body|test($re;"i"))' <<<"$maint" >/dev/null && reasons+=("maintainer doubt language")
jq -e --arg re "$okay_re" 'any(.[];.body|test($re;"i"))' <<<"$maint" >/dev/null && approval+=("maintainer comment: welcome/confirmed")
for l in $(jq -r '.labels[].name' <<<"$iss" | tr ' ' '_'); do
  case "$(printf %s "$l" | tr A-Z a-z)" in *accepted*|*approved*|*triaged*|*confirmed*|*help_wanted*|*good_first*) approval+=("label:$l");; esac
done

last=$(jq -r --argjson now "$now" '[.[]|.createdAt|fromdateiso8601]|max // null|if .==null then null else (($now-.)/86400|floor) end' <<<"$maint")
[ "${#approval[@]}" -gt 0 ] || reasons+=("no maintainer approval signal")
[ "$last" = null ] || [ "$last" -le 180 ] || reasons+=("maintainer silent ${last}d")

verdict=PASS; [ "${#reasons[@]}" -eq 0 ] || verdict=REJECT
jq -nc --arg i "$repo#$n" --arg v "$verdict" --arg last "$last" \
  --argjson r "$(printf '%s\n' "${reasons[@]:-}" | jq -R . | jq -sc 'map(select(.!=""))')" \
  --argjson a "$(printf '%s\n' "${approval[@]:-}" | jq -R . | jq -sc 'map(select(.!=""))')" \
  '{issue:$i,verdict:$v,reasons:$r,approval:$a,last_maintainer_comment_days:(try ($last|tonumber) catch null)}'
