#!/usr/bin/env bash
# Record test evidence. Usage:
#   evidence.sh before <file> -- <cmd...>   run WITH the fix reverted; expected to fail
#   evidence.sh after  <file> -- <cmd...>   run WITH the fix applied; must pass
#   evidence.sh note   <file> "<text>"      e.g. "NO-BEFORE: new feature, nothing to fail"
# Each run appends the command, exit code and the output tail to <file>.
set -uo pipefail
mode=$1; file=$2; shift 2
if [ "$mode" = note ]; then printf '\n%s\n' "$*" >> "$file"; exit 0; fi
[ "${1:-}" = "--" ] && shift
tag=$(printf '%s' "$mode" | tr a-z A-Z)
out=$("$@" 2>&1); rc=$?
{
  printf '\n## %s  (%s)\n$ %s\nexit=%s\n```\n' "$tag" "$(date -u +%FT%TZ)" "$*" "$rc"
  printf '%s\n' "$out" | tail -40
  printf '```\n'
} >> "$file"
printf '%s\n' "$out" | tail -15
echo "[evidence] $tag exit=$rc recorded in $file"
exit $rc
