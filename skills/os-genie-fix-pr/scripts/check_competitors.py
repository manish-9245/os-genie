#!/usr/bin/env python3
"""Competitor gate: refuse to open a PR when someone else already has one for the same issue.

Usage: check_competitors.py <owner/repo> <body.md>   (issue numbers come from Fixes/Closes/Resolves #N in the body)
Looks at every PR (open, or merged/closed in the last 14 days) that mentions the issue, from anyone but the fork owner.
Run right before opening, not at triage time: utopia#1381 appeared hours after triage and won on completeness.
Exit 0 clear, 1 blocked.
"""
import json, re, subprocess, sys, datetime
repo, body = sys.argv[1], open(sys.argv[2], encoding="utf-8").read()
nums = sorted(set(re.findall(r"(?i)\b(?:fix(?:e[sd])?|close[sd]?|resolve[sd]?)\s*:?\s*#(\d+)", body)))
me = subprocess.run(["gh", "api", "user", "--jq", ".login"], capture_output=True, text=True).stdout.strip()
if not nums: print("WARN: no 'Fixes #N' in the body, cannot check competitors"); sys.exit(0)
bad = []
for n in nums:
    out = subprocess.run(["gh", "pr", "list", "--repo", repo, "--state", "all", "--search", f"{n} in:title,body", "--json", "number,state,author,title,closedAt,mergedAt", "--limit", "20"], capture_output=True, text=True).stdout
    for p in json.loads(out or "[]"):
        if p["author"]["login"] == me: continue
        recent = (p["closedAt"] or "9999")[:10] >= (datetime.date.today() - datetime.timedelta(days=14)).isoformat()
        if p["state"] == "OPEN" or p["mergedAt"] or recent: bad.append(f"#{n}: PR #{p['number']} {p['state']} by {p['author']['login']}: {p['title'][:60]}")
if bad: print("BLOCKED: another PR already addresses this issue:"); [print(" -", b) for b in bad]; sys.exit(1)
print("PASS: no competing PRs for", ", ".join("#" + n for n in nums))
