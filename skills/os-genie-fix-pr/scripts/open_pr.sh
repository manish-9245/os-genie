#!/usr/bin/env bash
# The ONLY sanctioned way to open a PR. Runs the body gate first.
# Usage: open_pr.sh <upstream owner/repo> <fork-owner:branch> <base> "<title>" <body.md> [--draft]
set -uo pipefail
repo=$1; head=$2; base=$3; title=$4; body=$5; shift 5
here=$(cd "$(dirname "$0")" && pwd)
python3 "$here/check_pr_body.py" "$repo" "$body"; rc=$?
if [ $rc -eq 3 ]; then echo "STOPPED: human-submit repo. Not creating the PR."; exit 3; fi
if [ $rc -ne 0 ]; then echo "STOPPED: fix the PR body and retry."; exit 1; fi
gh pr create --repo "$repo" --head "$head" --base "$base" --title "$title" --body-file "$body" "$@"
