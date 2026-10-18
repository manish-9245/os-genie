#!/usr/bin/env python3
"""Org cap gate for os-genie-fix-pr: at most 2 PRs per upstream org per day.

Usage: check_caps.py <owner/repo>
Reads ~/oss-genie/ledger.json (every PR opened through open_pr.sh). Exit 1 when the
org already has 2 PRs opened today. Override only with a stated reason:
OSG_CAP_OVERRIDE="reason" (printed, never silent).
Why: 10 PRs opened in about an hour to freeCodeCamp on 2026-10-16 were all closed by a
maintainer within 1 to 3 minutes each, no comment. Bursts look like spam even when each PR is fine.
"""
import datetime, json, os, sys

CAP = 2
repo = sys.argv[1]
org = repo.split("/")[0].lower()
today = datetime.date.today().isoformat()
try:
    prs = json.load(open(os.path.expanduser("~/oss-genie/ledger.json")))["prs"]
except (OSError, ValueError, KeyError):
    prs = {}
n = sum(1 for k, p in prs.items()
        if k.split("/")[0].lower() == org and (p.get("opened") or "").startswith(today))
if n >= CAP:
    why = os.environ.get("OSG_CAP_OVERRIDE", "").strip()
    if why:
        print(f"cap override ({n} PRs to {org} today): {why}")
        sys.exit(0)
    print(f"BLOCKED: {n} PRs already opened to {org} today (cap {CAP}). "
          "Wait for a maintainer response before opening more, or set OSG_CAP_OVERRIDE=\"reason\".")
    sys.exit(1)
print(f"ok: {n}/{CAP} PRs to {org} today")
