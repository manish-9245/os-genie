#!/usr/bin/env bash
# verify_pr.sh: pre-PR hygiene gate for os-genie-fix-pr. Fails loudly on red flags.
# Usage: bash scripts/verify_pr.sh [--base main]
set -euo pipefail
BASE="main"
if [ "${1:-}" = "--base" ]; then BASE="${2:-main}"; fi

fail=0
say() { printf '%s\n' "$*"; }
bad() { printf 'FAIL: %s\n' "$*"; fail=1; }
ok()  { printf 'ok: %s\n' "$*"; }

# 1. Branch guard
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
  bad "on $BRANCH: create a feature branch (type/slug)"
else
  ok "branch $BRANCH"
fi

# 2. Secrets sweep (staged + unstaged diff)
if git diff --cached --diff-filter=ACM -U0 2>/dev/null | grep -niE '(api_key|apikey|password|secret|token)\s*[:=]' >/dev/null; then
  bad "possible secret assignment in staged diff: remove before pushing"
else
  ok "no secret patterns in staged diff"
fi
if git diff -U0 2>/dev/null | grep -niE '(api_key|apikey|password|secret|token)\s*[:=]' >/dev/null; then
  bad "possible secret assignment in unstaged diff: remove before pushing"
else
  ok "no secret patterns in unstaged diff"
fi

# 3. Debug leftovers
if git diff --cached --diff-filter=ACM 2>/dev/null | grep -nE 'console\.log|print\(|debugger|TODO|FIXME' >/dev/null; then
  bad "debug/TODO markers in staged diff: clean up"
else
  ok "no debug markers in staged diff"
fi

# 4. Diff-size guard vs base (LinearB bands: 50 ideal / 200 good / 400 max)
ADDED=0; REMOVED=0
if git rev-parse --verify "$BASE" >/dev/null 2>&1; then
  STAT="$(git diff --shortstat "$BASE"...HEAD 2>/dev/null || true)"
  ADDED="$(printf '%s' "$STAT" | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+' || echo 0)"
  REMOVED="$(printf '%s' "$STAT" | grep -oE '[0-9]+ deletion' | grep -oE '[0-9]+' || echo 0)"
  TOTAL=$((ADDED + REMOVED))
  say "diff vs $BASE: +$ADDED -$REMOVED (total $TOTAL)"
  if [ "$TOTAL" -gt 400 ]; then
    bad "diff >400 lines: split the PR or justify in body"
  elif [ "$TOTAL" -gt 200 ]; then
    say "WARN: diff >200 lines, expect slower review"
  else
    ok "diff size in reviewable band"
  fi
else
  say "WARN: base $BASE not found, skipping size guard"
fi

# 5. CI status if gh available and PR exists
if command -v gh >/dev/null 2>&1 && gh pr view --json number -q .number >/dev/null 2>&1; then
  say "--- gh pr checks ---"
  gh pr checks || bad "CI checks failing: fix before requesting review"
else
  say "WARN: no gh PR context, run 'gh pr checks' after pushing"
fi

if [ "$fail" -eq 0 ]; then say "PASS: ready to open PR"; else say "BLOCKED: fix FAIL lines above"; fi
exit "$fail"
