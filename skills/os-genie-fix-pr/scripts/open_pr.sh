#!/usr/bin/env bash
# The ONLY sanctioned way to open a PR. Run from inside the local clone of the fix.
# Usage: open_pr.sh <upstream owner/repo> <fork-owner:branch> <base> "<title>" <body.md> <evidence-file|docs-only> [gh pr create flags]
# Gates, in order: evidence (code needs local test evidence), PR body (template, policy, dashes,
# no AI branding unless the repo asks), then creates the PR and runs the CLA step.
set -uo pipefail
repo=$1; head=$2; base=$3; title=$4; body=$5; evidence=$6; shift 6
here=$(cd "$(dirname "$0")" && pwd)
python3 "$here/check_evidence.py" "$evidence" "upstream/${base}" || { echo "STOPPED: evidence gate. Fix and retest locally."; exit 1; }
python3 "$here/check_pr_body.py" "$repo" "$body"; rc=$?
if [ $rc -eq 3 ]; then echo "STOPPED: human-submit repo. Not creating the PR."; exit 3; fi
if [ $rc -ne 0 ]; then echo "STOPPED: fix the PR body and retry."; exit 1; fi
case "$title$(cat "$body")" in *$'\xe2\x80\x94'*|*$'\xe2\x80\x93'*) echo "STOPPED: em/en dash in title"; exit 1;; esac
url=$(gh pr create --repo "$repo" --head "$head" --base "$base" --title "$title" --body-file "$body" "$@") || exit 1
echo "$url"
n=${url##*/}
lg="$here/ledger.py"
python3 "$lg" register "$repo#$n" --clone "$(pwd)" --evidence "$evidence" >/dev/null
python3 "$lg" note "$repo#$n" "opened: $title" >/dev/null
python3 "$here/cla_sign.py" "$repo" "$n"
python3 "$lg" sync "$repo#$n" >/dev/null 2>&1; python3 "$lg" site >/dev/null 2>&1
# after a PR is MERGED (and only then): python3 "$lg" cleanup --apply   (deletes that PR's local clone)   # posts the signing comment if the CLA is comment-based; else prompts the owner
