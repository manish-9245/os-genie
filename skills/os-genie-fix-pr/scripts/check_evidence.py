#!/usr/bin/env python3
"""Evidence gate: code PRs need real local test evidence. Docs-only diffs are exempt.

Usage: check_evidence.py <evidence-file|docs-only> [base-ref]   (run inside the clone)
Passes only when, for any non-doc change, the evidence file has:
  - at least one AFTER block with exit=0 (tests/build/lint passing with the fix), and
  - at least one BEFORE block with a non-zero exit (the repro/test failing without the fix)
    OR an explicit line 'NO-BEFORE: <reason>' (new feature, refactor, nothing to fail).
Exit 0 ok, 1 blocked.
"""
import re, subprocess, sys
DOC = re.compile(r"\.(md|rst|txt|adoc)$|^docs?/|(^|/)(LICENSE|CHANGELOG)", re.I)
arg = sys.argv[1] if len(sys.argv) > 1 else ""
base = sys.argv[2] if len(sys.argv) > 2 else "origin/HEAD"
files = subprocess.run(["git", "diff", "--name-only", f"{base}...HEAD"], capture_output=True, text=True).stdout.split()
code = [f for f in files if not DOC.search(f)]
if not code:
    print("PASS: docs-only diff, no test evidence required"); sys.exit(0)
if arg in ("", "docs-only"):
    print(f"BLOCKED: diff touches code ({', '.join(code[:4])}) but no evidence file given."); sys.exit(1)
try: ev = open(arg, encoding="utf-8").read()
except OSError: print(f"BLOCKED: evidence file {arg} not found"); sys.exit(1)
blocks = re.findall(r"^## (BEFORE|AFTER)[^\n]*\n\$ ([^\n]*)\nexit=(\d+)", ev, re.M)
after_ok = [b for b in blocks if b[0] == "AFTER" and b[2] == "0"]
before_fail = [b for b in blocks if b[0] == "BEFORE" and b[2] != "0"]
problems = []
if not after_ok: problems.append("no AFTER block with exit=0 (tests must pass with the fix applied)")
if not before_fail and not re.search(r"^NO-BEFORE:\s*\S+", ev, re.M):
    problems.append("no BEFORE block with a failing exit, and no 'NO-BEFORE: <reason>' line")
hc = re.findall(r"^## HUNK-CHECK[^\n]*\n\$[^\n]*\nuncovered=(\d+)", ev, re.M)
waivers = len(re.findall(r"^HUNK-WAIVER:\s*\S+", ev, re.M))
if not hc: problems.append("no HUNK-CHECK block: run scripts/hunk_check.py (every source hunk must be needed by a test)")
elif int(hc[-1]) > waivers: problems.append(f"HUNK-CHECK left {hc[-1]} uncovered hunk(s) with {waivers} HUNK-WAIVER line(s): add a test that fails without each hunk, or delete the hunk")
if problems:
    print("BLOCKED: test evidence is incomplete:"); [print(" -", p) for p in problems]
    print("Record it with scripts/evidence.sh before|after <file> -- <cmd>. No evidence, no PR (no draft fallback)."); sys.exit(1)
print(f"PASS: {len(after_ok)} passing AFTER run(s), {len(before_fail)} failing BEFORE run(s)")
