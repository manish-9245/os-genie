#!/usr/bin/env python3
"""PR-body gate for os-genie-fix-pr. Blocks the numpy#33046 failure class.

Usage: check_pr_body.py <owner/repo> <body.md> [--show-template]
Exit 0 = body matches the repo's real PR template and policy; 1 = fix the body;
3 = HUMAN_SUBMIT (repo requires a human to create the PR / write the text).

Checks (all from the upstream repo, never from memory):
  1. Every heading of the repo's PR template is present in the body, in order,
     with real (non-comment, non-blank) content under it.
  2. Only if the repo's own template/CONTRIBUTING/AI policy asks for AI
     disclosure, the body contains a short one in the repo's format. No AI
     branding is added anywhere else. No em or en dashes allowed.
  3. Attestation checkboxes ("I wrote this myself", "without relying on an AI",
     "tested on a live environment") are NOT ticked by the agent.
  4. Repos that require human submission/communication => exit 3.
Stdlib + gh only.
"""
import base64, json, re, subprocess, sys

TEMPLATES = [".github/PULL_REQUEST_TEMPLATE.md", ".github/pull_request_template.md",
             "PULL_REQUEST_TEMPLATE.md", "pull_request_template.md",
             "docs/PULL_REQUEST_TEMPLATE.md", "docs/pull_request_template.md"]
POLICY_FILES = ["CONTRIBUTING.md", ".github/CONTRIBUTING.md", "AI_POLICY.md",
                ".github/AI_POLICY.md", "AGENTS.md", "docs/CONTRIBUTING.md"]
HUMAN_RE = re.compile(
    r"(must be performed by humans|(PR descriptions|pull request descriptions)[^.\n]{0,80}(from|by) humans|to be from humans|including the submission of (PRs|pull requests)|"
    r"written by a human|human[- ]written|PRs? (must|should) be (opened|submitted|created) by (a )?human|"
    r"no LLMs?\b|AI[- ]generated contributions are not permitted|do not use (AI|LLM)s? (to|for) "
    r"(respond|reply|communicat|writ))", re.I)
AI_RE = re.compile(r"\b(AI|LLM|LLMs|Copilot|ChatGPT|Claude|generative)\b", re.I)
DISC_RE = re.compile(
    r"((disclos|indicate|declare|mention|state|tell us|let us know|note)[^\n]{0,120}\b(AI|LLM|Copilot|ChatGPT|generative)\b|"
    r"\b(AI|LLM|Copilot|ChatGPT|generative)\b[^\n]{0,120}(disclos|must be (indicated|declared|mentioned)|should be (indicated|declared|mentioned)))", re.I)
ATTEST_RE = re.compile(
    r"(without relying on an? (AI|LLM)|i (wrote|authored)[^\n]{0,40}(myself|by hand)|human[- ]authored|"
    r"tested (my changes )?on a live|reviewed every (line|change)|take full responsibility|"
    r"understand the (submitted )?changes)", re.I)

def gh_file(repo, path):
    r = subprocess.run(["gh", "api", f"repos/{repo}/contents/{path}", "--jq", ".content"],
                       capture_output=True, text=True)
    if r.returncode or not r.stdout.strip():
        return None
    try:
        return base64.b64decode(r.stdout).decode("utf-8", "replace")
    except Exception:
        return None

def strip_comments(t):
    return re.sub(r"<!--.*?-->", "", t, flags=re.S)

HEAD_RE = r"^(?:(#{1,6})\s+(.+?)\s*#*|\*\*(.+?)\*\*:?)\s*$"

def _name(m):
    return (m.group(2) or m.group(3)).strip().lower()

def _level(m):
    return len(m.group(1)) if m.group(1) else 7

def headings(t):
    return [_name(m) for m in re.finditer(HEAD_RE, strip_comments(t), re.M)]

def sections(body):
    """Return list of (heading_lower, content) from the body."""
    clean = strip_comments(body)
    ms = list(re.finditer(HEAD_RE, clean, re.M))
    out = []
    for i, m in enumerate(ms):
        end = len(clean)
        for m2 in ms[i + 1:]:
            if _level(m2) <= _level(m):   # same or higher level closes this section
                end = m2.start(); break
        out.append((_name(m), clean[m.end():end].strip()))
    return out

def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(2)
    repo, bodyf = sys.argv[1], sys.argv[2]
    show = "--show-template" in sys.argv
    body = "" if show else open(bodyf, encoding="utf-8").read()
    tmpl = next((t for t in (gh_file(repo, p) for p in TEMPLATES) if t), None)
    policy = {p: gh_file(repo, p) for p in POLICY_FILES}
    policy = {k: v for k, v in policy.items() if v}
    if "--show-template" in sys.argv:
        print(tmpl or "(no PR template found)"); sys.exit(0)

    problems, notes = [], []

    # 4. human-submission repos
    for name, txt in ([("PR template", tmpl)] if tmpl else []) + list(policy.items()):
        m = HUMAN_RE.search(txt)
        if m:
            print(f"HUMAN_SUBMIT: {name} says: ...{m.group(0)}...")
            print("An agent must not create the PR or write its description for this repo.")
            print(f"Hand the owner the branch + {bodyf} as a DRAFT of facts only; the owner writes and posts.")
            sys.exit(3)

    # 1. template fidelity
    if tmpl:
        want = headings(tmpl)
        have = sections(body)
        have_names = [h for h, _ in have]
        pos = -1
        for h in want:
            if h not in have_names[pos + 1:]:
                problems.append(f"missing or out-of-order template section: '{h}'")
                continue
            pos = have_names.index(h, pos + 1)
            content = have[pos][1]
            if len(re.sub(r"[\s\-\*\[\]xX]+", "", content)) < 3:
                problems.append(f"template section '{h}' is empty")
    else:
        notes.append("no PR template in repo: use templates/pull-request.md")

    # 2. AI disclosure, ONLY where the repo's own rules ask for one
    rule_txts = ([strip_comments(tmpl)] if tmpl else []) + [v for k, v in policy.items() if k != "AGENTS.md"]
    needs_disc = any(DISC_RE.search(t) for t in rule_txts)
    if needs_disc and not re.search(r"(AI[- ]assisted|Claude|LLM|AI tool|generated with|written with)", strip_comments(body), re.I):
        problems.append("the repo's rules ask for AI disclosure but the body has none (use the repo's own format, keep it short)")
    # 2b. style: no em/en dashes anywhere in the body
    if re.search("[\u2014\u2013]", body):
        problems.append("body contains an em dash or en dash: remove it (owner rule)")

    # 3. attestation boxes the agent must not tick
    for line in body.splitlines():
        if re.match(r"\s*[-*]\s*\[[xX]\]", line) and ATTEST_RE.search(line):
            problems.append(f"agent ticked an attestation box it cannot truthfully give: {line.strip()[:90]}")

    for n in notes: print("note:", n)
    if problems:
        print("BLOCKED: PR body does not satisfy the repo's rules:")
        for p in problems: print(" -", p)
        print("Fix: start from the repo template ( --show-template ), fill EVERY section, then re-run.")
        sys.exit(1)
    print("PASS: body matches the repo template and policy")

main()
