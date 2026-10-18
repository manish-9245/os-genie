#!/usr/bin/env python3
"""Self-check: approval counts only maintainer comments. Run: python3 test_score_issue.py"""
import json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

def score(comment_role):
    issue = {"number": 1, "labels": [], "assignees": [], "milestone": None,
             "createdAt": "2026-10-01T00:00:00Z", "updatedAt": "2026-10-10T00:00:00Z",
             "body": "Steps to repro. Expected 1 actual 2 in `src/a.py`, version 1.2, error log.",
             "comments": [{"author": {"login": "x"}, "authorAssociation": comment_role,
                           "createdAt": "2026-10-10T00:00:00Z", "body": "confirmed, PR welcome"}]}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(issue, f)
    out = subprocess.run([sys.executable, os.path.join(HERE, "score_issue.py"), f.name,
                          "--now=2026-10-18"], capture_output=True, text=True).stdout
    os.unlink(f.name)
    return json.loads(out)["breakdown"]["approval"]["pts"]

assert score("NONE") == 0, "outside contributor must not grant approval"
assert score("CONTRIBUTOR") == 0
assert score("MEMBER") == 35
assert score("COLLABORATOR") == 35
print("ok")
