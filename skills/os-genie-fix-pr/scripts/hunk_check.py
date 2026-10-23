#!/usr/bin/env python3
"""Per-hunk mutation check: every non-test source hunk must be needed by at least one test.

Usage: hunk_check.py <base-ref> <evidence-file> -- <test cmd...>   (run in the clone, clean worktree, fix committed)
For each source hunk of `git diff base...HEAD` it reverts that hunk alone, runs the test cmd, and restores.
A hunk whose revert leaves the tests green is UNCOVERED: no test depends on it. Add a test that fails
without it, or delete the hunk (razor test), or record a one-line `HUNK-WAIVER: <file>:<line> <reason>` in the
evidence file and list it under "Not covered by tests" in the PR body.
Appends a `## HUNK-CHECK` block to the evidence file. Exit 0 only when uncovered=0.
Built after utopia#1380: three of seven hunks (the embed paths) had no test and the PR body claimed they did.
"""
import re, subprocess, sys, tempfile, os
TEST = re.compile(r"(^|/)(tests?|spec|__tests__)/|[._-](tests?|spec)\.|_test\.|test_[^/]*\.|Tests?\.java$|Test\.kt$", re.I)
DOC = re.compile(r"\.(md|rst|txt|adoc|json|ya?ml|toml|lock)$|^docs?/|(^|/)(LICENSE|CHANGELOG)", re.I)
if "--" not in sys.argv or len(sys.argv) < 5: sys.exit(__doc__)
i = sys.argv.index("--"); base, ev = sys.argv[1], sys.argv[2]; cmd = sys.argv[i + 1:]
sh = lambda *a, **k: subprocess.run(a, capture_output=True, text=True, **k)
if sh("git", "status", "--porcelain").stdout.strip(): sys.exit("worktree not clean: commit the fix first")
diff = sh("git", "diff", "-U0", "--no-color", f"{base}...HEAD").stdout
hunks = []
for fchunk in re.split(r"(?m)^(?=diff --git )", diff):
    m = re.match(r"diff --git a/(\S+) b/(\S+)", fchunk)
    if not m or TEST.search(m.group(2)) or DOC.search(m.group(2)): continue
    head, *parts = re.split(r"(?m)^(?=@@ )", fchunk)
    for p in parts:
        ln = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)", p).group(1)
        hunks.append((m.group(2), ln, head + p))
if not hunks: sys.exit("no source hunks to check")
print(f"{len(hunks)} source hunk(s); test cmd: {' '.join(cmd)}")
base_rc = subprocess.run(cmd, capture_output=True, text=True).returncode
if base_rc: sys.exit("tests fail with the full fix applied; fix that first")
rows, unc = [], 0
for f, ln, patch in hunks:
    with tempfile.NamedTemporaryFile("w", suffix=".patch", delete=False) as t: t.write(patch if patch.endswith("\n") else patch + "\n")
    ap = sh("git", "apply", "-R", "--unidiff-zero", t.name)
    if ap.returncode: rows.append((f, ln, "SKIP (could not revert alone: " + ap.stderr.strip()[:60] + ")")); unc += 1; os.unlink(t.name); continue
    rc = subprocess.run(cmd, capture_output=True, text=True).returncode
    sh("git", "checkout", "--", "."); os.unlink(t.name)
    ok = rc != 0
    rows.append((f, ln, "covered (tests fail without it)" if ok else "UNCOVERED (tests still pass without it)")); unc += not ok
    print(f"  {f}:{ln} {rows[-1][2]}")
with open(ev, "a", encoding="utf-8") as fh:
    fh.write(f"\n## HUNK-CHECK  \n$ {' '.join(cmd)}\nuncovered={unc}\n```\n" + "\n".join(f"{f}:{ln} {s}" for f, ln, s in rows) + "\n```\n")
print(f"HUNK-CHECK uncovered={unc}"); sys.exit(1 if unc else 0)
