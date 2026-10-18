#!/usr/bin/env python3
"""Deterministic issue scorer for os-genie-issue-triage.

Usage:
    gh issue view <n> --repo <owner/repo> \
      --json number,title,labels,assignees,comments,createdAt,updatedAt,body,state,milestone > issue.json
    python3 score_issue.py issue.json [--now YYYY-MM-DD]

Reads gh JSON (single object or list with one object) and prints a 0-100
breakdown matching references/scoring-rubric.md. Stdlib only.

Approval signals count only when they come from a maintainer: a comment whose
authorAssociation is OWNER, MEMBER or COLLABORATOR. A "confirmed" or "go ahead"
from anyone else is a contributor talking, not approval (incident 2026-10-18:
only 2 of 46 issues scored 100 had a real maintainer confirmation).
"""
import json
import re
import sys
from datetime import datetime, timezone

APPROVAL_LABELS = {"triaged", "confirmed", "accepted", "approved"}
INVITE_LABELS = {"help wanted", "good first issue"}
REJECT_LABELS = {"wontfix", "invalid", "duplicate"}

MAINTAINER_ROLES = {"OWNER", "MEMBER", "COLLABORATOR"}
MAINTAINER_PHRASES = [
    "confirmed", "repro confirmed", "good to go", "pr welcome",
    "accepting pr", "accepted", "go ahead",
]


def days_between(a, b):
    return (b - a).days


def parse_dt(s):
    if not s:
        return None
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "-"
    now = datetime.now(timezone.utc)
    for arg in sys.argv[2:]:
        if arg.startswith("--now="):
            now = datetime.fromisoformat(arg.split("=", 1)[1])
            if now.tzinfo is None:
                now = now.replace(tzinfo=timezone.utc)

    raw = sys.stdin.read() if path == "-" else open(path).read()
    try:
        data = json.loads(raw.strip() or "null")
    except json.JSONDecodeError:
        print(json.dumps({"score": 0, "verdict": "ERROR",
                          "reasons": ["unreadable issue JSON: re-run gh issue view"]}, indent=2))
        return 3
    if not isinstance(data, (dict, list)):
        print(json.dumps({"score": 0, "verdict": "ERROR",
                          "reasons": ["empty issue JSON: re-run gh issue view"]}, indent=2))
        return 3
    issue = data[0] if isinstance(data, list) else data

    labels = {l["name"].lower() if isinstance(l, dict) else str(l).lower()
              for l in issue.get("labels", [])}
    body = issue.get("body", "") or ""
    comments = issue.get("comments", []) or []
    assignees = issue.get("assignees", []) or []
    milestone = issue.get("milestone")
    updated = parse_dt(issue.get("updatedAt"))
    created = parse_dt(issue.get("createdAt"))

    # --- Hard rejects ---
    rejects = []
    if labels & REJECT_LABELS:
        rejects.append("reject label: %s" % sorted(labels & REJECT_LABELS))
    if assignees:
        rejects.append("already assigned")
    if rejects:
        print(json.dumps({"score": 0, "verdict": "REJECT",
                          "reasons": rejects}, indent=2))
        return 1

    # --- 1. Approval 0-35 ---
    maint = [c for c in comments
             if (c.get("authorAssociation") or "").upper() in MAINTAINER_ROLES]
    maint_text = " ".join((c.get("body", "") or "") for c in maint).lower()
    maintainer_hit = any(p in maint_text for p in MAINTAINER_PHRASES)
    age_days = days_between(created, now) if created else 999
    upd_days = days_between(updated, now) if updated else 999
    maint_dates = [parse_dt(c.get("createdAt")) for c in maint]
    recent = any(d and days_between(d, now) <= 30 for d in maint_dates)
    if comments and not any("authorAssociation" in c for c in comments):
        print("note: comments carry no authorAssociation, approval from comments "
              "cannot be verified: re-run gh issue view with the comments field",
              file=sys.stderr)
    if maintainer_hit:
        approval, why_a = 35, "maintainer (OWNER/MEMBER/COLLABORATOR) confirm phrase in thread"
    elif labels & APPROVAL_LABELS:
        approval, why_a = 25, "triaged/confirmed/accepted label or milestone"
    elif milestone:
        approval, why_a = 25, "milestone assigned"
    elif (labels & INVITE_LABELS) and recent:
        approval, why_a = 18, "help-wanted + maintainer reply <30d"
    elif labels & INVITE_LABELS:
        approval, why_a = 10, "beginner label only"
    else:
        approval, why_a = 0, "no maintainer signal"

    # --- 2. Scope clarity 0-25 ---
    low = body.lower()
    has_repro = bool(re.search(r"repro|steps to|expected.*actual|acceptance", low))
    has_expected = "expected" in low and "actual" in low
    has_area = bool(re.search(r"file|package|module|`[^`]+`|src/|lib/", low))
    if has_repro and (has_expected or has_area):
        clarity, why_c = 25, "repro + expected/actual or area pointer"
    elif has_repro:
        clarity, why_c = 15, "partial scope (repro or criteria only)"
    elif len(body.strip()) > 200:
        clarity, why_c = 8, "narrative only, no repro/criteria"
    else:
        clarity, why_c = 0, "one-liner, no scope"

    # --- 3. Freshness 0-20 ---
    if upd_days <= 60 and (recent or maintainer_hit):
        fresh, why_f = 20, "active <60d"
    elif upd_days <= 90:
        fresh, why_f = 12, "activity 60-90d"
    elif upd_days <= 180 and (labels & APPROVAL_LABELS or milestone):
        fresh, why_f = 6, "90-180d but still confirmed"
    else:
        fresh, why_f = 0, "stale >180d"

    # --- 4. Collision 0-10 ---
    claiming = any("working on" in (c.get("body", "") or "").lower()
                   for c in comments[-5:])
    collision, why_l = (0, "active claim in thread") if claiming else (10, "no assignee/claim")

    # --- 5. Evidence 0-10 ---
    has_version = bool(re.search(r"v?\d+\.\d+|version|os:|environment", low))
    has_logs = bool(re.search(r"stack|trace|error|log|```", low))
    evidence = (10 if has_version and has_logs else
                5 if has_version or has_logs else 0)
    why_e = "version+logs" if evidence == 10 else ("partial" if evidence else "none")

    total = approval + clarity + fresh + collision + evidence
    verdict = "RECOMMEND" if total >= 60 else "ASK-FIRST"
    print(json.dumps({
        "issue": issue.get("number"),
        "score": total,
        "verdict": verdict,
        "breakdown": {
            "approval": {"pts": approval, "why": why_a},
            "clarity": {"pts": clarity, "why": why_c},
            "freshness": {"pts": fresh, "why": why_f},
            "collision": {"pts": collision, "why": why_l},
            "evidence": {"pts": evidence, "why": why_e},
        },
        "issue_age_days": age_days,
        "updated_days_ago": upd_days,
    }, indent=2))
    return 0 if verdict == "RECOMMEND" else 2


if __name__ == "__main__":
    sys.exit(main())
