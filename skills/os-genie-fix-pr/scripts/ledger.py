#!/usr/bin/env python3
"""os-genie ledger: notes + PR state + local site. Data lives in ~/oss-genie (outside the repo).

  ledger.py sync [REPO#N ...]          pull live state of every PR you authored since the hunt start (~/oss-genie/config.json "since", default 2026-10-13)
  ledger.py register REPO#N [--clone PATH] [--evidence PATH] [--issue N] [--owner-action TEXT]
  ledger.py note REPO#N "text"         append a dated note (also written to notes.md)
  ledger.py site                       build ~/oss-genie/site/index.html
  ledger.py serve [port]               serve the site on http://localhost:8787
  ledger.py inbox [--mark]             list what each open PR is waiting on: reviews, comments, CI, conflicts, CLA (writes inbox.md)
  ledger.py cleanup [--apply]          delete local clones ONLY for PRs that are MERGED (verified live)
  ledger.py all                        sync + site (run this at the end of every task)
Stdlib + gh only.
"""
import json, os, re, subprocess, sys, shutil, datetime, html, pathlib

HOME = pathlib.Path.home() / "oss-genie"
LEDGER = HOME / "ledger.json"; NOTES = HOME / "notes.md"; SITE = HOME / "site"
HOME.mkdir(exist_ok=True)

def gh(*a):
    return subprocess.run(["gh", *a], capture_output=True, text=True)
def load():
    try: return json.loads(LEDGER.read_text())
    except Exception: return {"prs": {}}
def save(d): LEDGER.write_text(json.dumps(d, indent=1, sort_keys=True))
def now(): return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
def key(s):
    m = re.match(r"([^#\s]+)#(\d+)$", s)
    if not m: sys.exit(f"bad PR ref {s!r}, use owner/repo#123")
    return f"{m.group(1)}#{m.group(2)}"

def me():
    return gh("api", "user", "--jq", ".login").stdout.strip()

CLA_UNSIGNED = re.compile(r"(not[- ]signed|has not signed|have to sign|please sign|you can sign|before we can accept)", re.I)
CLA_SIGNED = re.compile(r"(all contributors have signed|have signed the cla|cla signed)", re.I)

def pr_state(repo, n, login):
    r = gh("pr", "view", str(n), "--repo", repo, "--json",
           "title,state,isDraft,mergedAt,closedAt,updatedAt,url,reviewDecision,statusCheckRollup,comments,additions,deletions,headRefName")
    if r.returncode: return None
    d = json.loads(r.stdout)
    failing = sorted({c.get("name") or c.get("context") for c in d.get("statusCheckRollup") or []
                      if (c.get("conclusion") or c.get("state")) in ("FAILURE", "ERROR", "TIMED_OUT")})
    cla = "n/a"
    last_other = None
    for c in d.get("comments") or []:
        a = (c.get("author") or {}).get("login", "")
        b = c.get("body") or ""
        if a.endswith("[bot]") or a in ("github-actions", "CLAassistant", "linux-foundation-easycla"):
            if re.search(r"(CLA|Contributor License)", b, re.I):
                cla = "signed" if (CLA_SIGNED.search(b) and not CLA_UNSIGNED.search(b)) else ("unsigned" if CLA_UNSIGNED.search(b) else cla)
        elif a and a != login:
            last_other = {"by": a, "at": c.get("createdAt", "")[:10], "text": b[:160]}
    state = "MERGED" if d.get("mergedAt") else ("CLOSED" if d["state"] == "CLOSED" else ("DRAFT" if d.get("isDraft") else "OPEN"))
    return {"title": d["title"], "state": state, "url": d["url"], "updated": d["updatedAt"][:10],
            "review": d.get("reviewDecision") or "", "failing": [f for f in failing if f], "cla": cla,
            "size": f"+{d.get('additions', 0)}/-{d.get('deletions', 0)}", "branch": d.get("headRefName", ""), "reply": last_other}

def cmd_sync(only=None):
    d = load(); login = me()
    cfg = HOME / "config.json"
    since = json.loads(cfg.read_text()).get("since", "2026-10-13") if cfg.exists() else "2026-10-13"
    r = gh("search", "prs", "--author", login, "--created", f">={since}", "--limit", "200", "--json", "number,repository")
    found = {f"{p['repository']['nameWithOwner']}#{p['number']}" for p in json.loads(r.stdout or "[]")}
    keys = sorted(found | set(d["prs"])) if not only else [key(o) for o in only]
    for k in keys:
        repo, n = k.rsplit("#", 1)
        st = pr_state(repo, n, login)
        if not st: continue
        e = d["prs"].setdefault(k, {"notes": [], "opened": now()})
        was = e.get("state")
        e.update(st); e["synced"] = now()
        if was and was != st["state"]:
            e["notes"].append(f"{now()} state {was} -> {st['state']}")
            with NOTES.open("a") as f: f.write(f"- {now()} {k}: {was} -> {st['state']}\n")
    save(d); print(f"synced {len(d['prs'])} PRs")

def cmd_register(args):
    k = key(args[0]); d = load(); e = d["prs"].setdefault(k, {"notes": [], "opened": now()})
    i = 1
    while i < len(args):
        flag = args[i]; val = args[i + 1] if i + 1 < len(args) else ""
        e[{"--clone": "clone", "--evidence": "evidence", "--issue": "issue", "--owner-action": "owner_action"}[flag]] = val; i += 2
    save(d); print("registered", k)

def cmd_note(args):
    k = key(args[0]); text = " ".join(args[1:]); d = load()
    d["prs"].setdefault(k, {"notes": [], "opened": now()})["notes"].append(f"{now()} {text}")
    with NOTES.open("a") as f: f.write(f"- {now()} {k}: {text}\n")
    save(d); print("noted")

def needs_you(e):
    out = []
    if e.get("state") in ("OPEN", "DRAFT"):
        if e.get("cla") == "unsigned": out.append("Sign the CLA")
        if e.get("failing"): out.append("Checks failing: " + ", ".join(e["failing"][:3]))
        if e.get("review") == "CHANGES_REQUESTED": out.append("Changes requested")
        if e.get("reply"): out.append(f"Reply from {e['reply']['by']} ({e['reply']['at']})")
    for it in e.get("inbox", []):
        if it["action"].startswith(("FIX", "REPLY", "OWNER")) and it["kind"] != "cla": out.append(f"{it['action'].split(' ')[0].title()}: {it['kind'].replace('_', ' ')} {it['by']}".strip())
    if e.get("owner_action"): out.append(e["owner_action"])
    return out


HUMAN_RE = re.compile(r"(must be performed by humans|including the submission of (PRs|pull requests)|written by a human|human[- ]written|"
                      r"(PR|pull request) descriptions[^.\n]{0,80}(from|by) humans|to be from humans|replies to reviewers should be written by a human|"
                      r"must not (create|open) (the )?(PR|pull request))", re.I)

def human_comms(repo):
    import base64
    for f in ("AGENTS.md", "CONTRIBUTING.md", ".github/CONTRIBUTING.md", "AI_POLICY.md", ".github/AI_POLICY.md", ".github/PULL_REQUEST_TEMPLATE.md", ".github/pull_request_template.md"):
        r = gh("api", f"repos/{repo}/contents/{f}", "--jq", ".content")
        if r.returncode or not r.stdout.strip(): continue
        try: t = base64.b64decode(r.stdout).decode("utf-8", "replace")
        except Exception: continue
        if HUMAN_RE.search(t): return True
    return False

def cmd_inbox(mark):
    """Find what each open PR is waiting on: reviews, maintainer comments, CI failures, conflicts, CLA."""
    d = load(); login = me(); lines = ["# Inbox (" + now() + " UTC)", ""]
    for k, e in sorted(d["prs"].items()):
        if e.get("state") not in ("OPEN", "DRAFT"): e["inbox"] = []; continue
        repo, n = k.rsplit("#", 1); since = e.get("seen_at", ""); items = []
        def js(path):
            r = gh("api", path, "--paginate"); 
            try: return json.loads(r.stdout or "[]")
            except Exception: return []
        IGN = {"CLAassistant", "vercel", "linux-foundation-easycla", "netlify", "codecov", "github-actions", "coderabbitai", "greptile-apps", "copilot-pull-request-reviewer"}
        def human(u): return u and u.get("login") != login and u.get("type") != "Bot" and not u.get("login", "").endswith("[bot]") and u.get("login") not in IGN
        for rv in js(f"repos/{repo}/pulls/{n}/reviews"):
            if human(rv.get("user")) and (rv.get("submitted_at") or "") > since and (rv.get("body") or rv["state"] == "CHANGES_REQUESTED"):
                items.append({"kind": "changes_requested" if rv["state"] == "CHANGES_REQUESTED" else "review", "by": rv["user"]["login"], "at": rv["submitted_at"][:10], "text": (rv.get("body") or "")[:300], "action": "FIX"})
        for c in js(f"repos/{repo}/pulls/{n}/comments"):
            if human(c.get("user")) and c["created_at"] > since:
                items.append({"kind": "inline_review", "by": c["user"]["login"], "at": c["created_at"][:10], "text": f"{c['path']}: {c['body'][:260]}", "action": "FIX"})
        for c in js(f"repos/{repo}/issues/{n}/comments"):
            if human(c.get("user")) and c["created_at"] > since:
                items.append({"kind": "comment", "by": c["user"]["login"], "at": c["created_at"][:10], "text": c["body"][:300], "action": "REPLY" if "?" in c["body"] else "READ"})
        v = gh("pr", "view", n, "--repo", repo, "--json", "mergeable,mergeStateStatus,statusCheckRollup")
        if v.returncode == 0:
            vv = json.loads(v.stdout)
            if vv.get("mergeable") == "CONFLICTING": items.append({"kind": "merge_conflict", "by": "", "at": now()[:10], "text": "Branch conflicts with base. Rebase in the local clone.", "action": "FIX"})
            bad = sorted({c.get("name") or c.get("context") for c in vv.get("statusCheckRollup") or [] if (c.get("conclusion") or c.get("state")) in ("FAILURE", "ERROR", "TIMED_OUT")})
            bad = [b for b in bad if b and not any(x in b.lower() for x in ("cla", "vercel", "netlify", "codecov"))]
            if bad: items.append({"kind": "ci_failing", "by": "", "at": now()[:10], "text": "Failing: " + ", ".join(bad[:4]), "action": "FIX"})
        if e.get("cla") == "unsigned": items.append({"kind": "cla", "by": "", "at": now()[:10], "text": "CLA unsigned", "action": "OWNER"})
        if "human" not in e: e["human"] = human_comms(repo)
        if e["human"]:
            for it in items:
                if it["action"] in ("REPLY",): it["action"] = "OWNER (repo wants human-written replies)"
        e["inbox"] = items
        if items:
            lines.append(f"## {k}  {e.get('title','')}" + ("  [human-written comms required]" if e["human"] else ""))
            lines.append(f"{e.get('url','')}  clone: {e.get('clone') or 'none (re-clone the fork branch ' + e.get('branch','') + ')'}")
            for it in items: lines.append(f"- [{it['action']}] {it['kind']} {it['by']} {it['at']}: {it['text']}".replace("\n", " "))
            lines.append("")
        if mark: e["seen_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    save(d); (HOME / "inbox.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines) if len(lines) > 2 else "inbox empty"); print("written:", HOME / "inbox.md")

def cmd_cleanup(apply):
    d = load(); login = me(); freed = 0
    for k, e in sorted(d["prs"].items()):
        p = e.get("clone")
        if not p or not os.path.isdir(p): continue
        repo, n = k.rsplit("#", 1)
        st = pr_state(repo, n, login)           # verify live, never trust the ledger
        if not st or st["state"] != "MERGED":
            print(f"keep   {k} ({st['state'] if st else 'unknown'}): {p}"); continue
        size = subprocess.run(["du", "-sk", p], capture_output=True, text=True).stdout.split()[0]
        print(f"{'DELETE' if apply else 'would delete'} {k} MERGED: {p} ({int(size)//1024} MB)")
        if apply:
            shutil.rmtree(p, ignore_errors=True); e["clone"] = ""; e["notes"].append(f"{now()} clone deleted after merge"); freed += int(size)
    if apply: save(d); print(f"freed ~{freed//1024} MB")

def cmd_site():
    d = load(); SITE.mkdir(exist_ok=True)
    rows = []
    for k, e in d["prs"].items():
        if not e.get("state"): continue
        rows.append({"key": k, **{x: e.get(x) for x in ("title", "state", "url", "updated", "size", "cla", "review", "failing", "clone", "evidence", "issue", "reply", "branch")},
                     "need": needs_you(e), "notes": e.get("notes", [])[-6:]})
    order = {"OPEN": 0, "DRAFT": 1, "MERGED": 2, "CLOSED": 3}
    rows.sort(key=lambda r: (0 if r["need"] else 1, order.get(r["state"], 9), r["updated"] or ""), reverse=False)
    counts = {s: sum(1 for r in rows if r["state"] == s) for s in order}
    counts["NEED"] = sum(1 for r in rows if r["need"] and r["state"] in ("OPEN", "DRAFT"))
    tpl = (pathlib.Path(__file__).parent / "site_template.html").read_text()
    payload = json.dumps({"rows": rows, "counts": counts, "built": now()}).replace("</", "<\\/")
    (SITE / "index.html").write_text(tpl.replace("/*DATA*/null", payload))
    print("site built:", SITE / "index.html", counts)

def cmd_serve(port="8787"):
    cmd_site(); print(f"open http://localhost:{port}  (Ctrl+C to stop)")
    os.chdir(SITE); subprocess.run([sys.executable, "-m", "http.server", port, "--bind", "127.0.0.1"])

def main():
    a = sys.argv[1:]
    if not a: print(__doc__); return
    c = a[0]
    if c == "sync": cmd_sync(a[1:] or None)
    elif c == "register": cmd_register(a[1:])
    elif c == "note": cmd_note(a[1:])
    elif c == "site": cmd_site()
    elif c == "serve": cmd_serve(*a[1:2])
    elif c == "cleanup": cmd_cleanup("--apply" in a)
    elif c == "inbox": cmd_inbox("--mark" in a)
    elif c == "all": cmd_sync(); cmd_site()
    else: print(__doc__)
main()
