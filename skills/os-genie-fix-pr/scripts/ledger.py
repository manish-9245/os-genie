#!/usr/bin/env python3
"""os-genie ledger: notes + PR state + local site. Data lives in ~/oss-genie (outside the repo).

  ledger.py sync [REPO#N ...]          pull live state of every PR you authored since the hunt start (~/oss-genie/config.json "since", default 2026-10-13)
  ledger.py register REPO#N [--clone PATH] [--evidence PATH] [--issue N] [--owner-action TEXT]
  ledger.py note REPO#N "text"         append a dated note (also written to notes.md)
  ledger.py site                       build the local site in ~/oss-genie/site (index.html, style.css, app.js, data.json)
  ledger.py publish [--deploy]         copy the site into ~/oss-progress-site/dist, and deploy it with wrangler when --deploy is given
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

IGN_USERS = {"CLAassistant", "vercel", "linux-foundation-easycla", "netlify", "codecov", "github-actions", "coderabbitai", "greptile-apps", "changeset-bot", "copilot-pull-request-reviewer"}
NOISE_CHECKS = ("cla", "vercel", "netlify", "codecov")

def pr_state(repo, n, login):
    r = gh("pr", "view", str(n), "--repo", repo, "--json",
           "title,state,isDraft,mergedAt,closedAt,updatedAt,url,reviewDecision,statusCheckRollup,comments,additions,deletions,headRefName")
    if r.returncode: return None
    d = json.loads(r.stdout)
    failing = sorted({c.get("name") or c.get("context") for c in d.get("statusCheckRollup") or []
                      if (c.get("conclusion") or c.get("state")) in ("FAILURE", "ERROR", "TIMED_OUT")
                      and not any(x in (c.get("name") or c.get("context") or "").lower() for x in NOISE_CHECKS)})
    cla = "n/a"
    last_other = None
    for c in d.get("comments") or []:
        a = (c.get("author") or {}).get("login", "")
        b = c.get("body") or ""
        if a.endswith("[bot]") or a in ("github-actions", "CLAassistant", "linux-foundation-easycla"):
            if re.search(r"(CLA|Contributor License)", b, re.I):
                cla = "signed" if (CLA_SIGNED.search(b) and not CLA_UNSIGNED.search(b)) else ("unsigned" if CLA_UNSIGNED.search(b) else cla)
        elif a and a != login and a not in IGN_USERS and "bot" not in a.lower():
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
        seen = set()
        for it in e.get("inbox", []):
            if it["kind"] == "cla" or it["action"] == "READ": continue
            label = {"changes_requested": "Changes requested", "review": "Review to answer", "inline_review": "Review comment to fix",
                     "comment": "Question to answer", "ci_failing": "CI failing", "merge_conflict": "Merge conflict"}.get(it["kind"], it["kind"])
            if label not in seen: seen.add(label); out.append(label + (f" ({it['by']})" if it["by"] else ""))
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

SITE_SRC = pathlib.Path(__file__).resolve().parent.parent / "site"
PUBLIC_DIR = pathlib.Path.home() / "oss-progress-site"

def waiting_words(e):
    """Plain, public-safe reasons a PR is waiting on the owner. No paths, no private notes."""
    out = []
    if e.get("state") in ("OPEN", "DRAFT"):
        if e.get("cla") == "unsigned": out.append("CLA to sign")
        kinds = {it["kind"] for it in e.get("inbox", []) if it["action"] != "READ" and it["kind"] != "cla"}
        for kind, word in (("changes_requested", "changes requested"), ("inline_review", "review comments to address"), ("review", "review to answer"),
                           ("comment", "question to answer"), ("ci_failing", "failing checks"), ("merge_conflict", "merge conflict")):
            if kind in kinds: out.append(word)
        if e.get("owner_action") and not out: out.append("something I still need to do")
    return out

def export_rows():
    rows = []
    for k, e in d_all().items():
        if not e.get("state"): continue
        repo, n = k.rsplit("#", 1)
        rows.append({"key": k, "repo": repo, "number": n, "title": e.get("title", ""), "url": e.get("url", ""), "state": e["state"],
                     "updated": e.get("updated", ""), "size": e.get("size", ""), "cla": e.get("cla", ""), "review": e.get("review", ""),
                     "failing": e.get("failing", []), "waiting": waiting_words(e)})
    rows.sort(key=lambda r: r["updated"], reverse=True)
    counts = {x: sum(1 for r in rows if r["state"] == x) for x in ("OPEN", "DRAFT", "MERGED", "CLOSED")}
    cfg = HOME / "config.json"
    since = json.loads(cfg.read_text()).get("since", "2026-10-13") if cfg.exists() else "2026-10-13"
    label = datetime.date.fromisoformat(since).strftime("%-d %B %Y")
    return {"rows": rows, "counts": counts, "built": now(), "since_label": label}

def d_all(): return load()["prs"]

def write_site(dest):
    dest = pathlib.Path(dest); dest.mkdir(parents=True, exist_ok=True)
    for f in ("index.html", "style.css", "app.js"): shutil.copy(SITE_SRC / f, dest / f)
    (dest / "data.json").write_text(json.dumps(export_rows(), indent=1))
    return dest

def cmd_site():
    dest = write_site(SITE); c = json.loads((dest / "data.json").read_text())["counts"]
    print("site built:", dest / "index.html", c)

def cmd_publish(deploy):
    """Copy the same site to ~/oss-progress-site/dist (replacing old files). data.json holds public-safe fields only."""
    dist = PUBLIC_DIR / "dist"
    if not PUBLIC_DIR.exists(): sys.exit("~/oss-progress-site not found")
    for old in dist.glob("*"):
        shutil.rmtree(old) if old.is_dir() else old.unlink()
    write_site(dist); print("copied to", dist)
    if not deploy: print("not deployed. Log in once with: npx wrangler login   then: ledger.py publish --deploy"); return
    cfg = HOME / "config.json"; env = dict(os.environ)
    if cfg.exists() and json.loads(cfg.read_text()).get("cloudflare_account_id"): env["CLOUDFLARE_ACCOUNT_ID"] = json.loads(cfg.read_text())["cloudflare_account_id"]
    r = subprocess.run(["npx", "-y", "wrangler", "deploy"], cwd=PUBLIC_DIR, env=env)
    sys.exit(r.returncode)

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
    elif c == "publish": cmd_publish("--deploy" in a)
    elif c == "serve": cmd_serve(*a[1:2])
    elif c == "cleanup": cmd_cleanup("--apply" in a)
    elif c == "inbox": cmd_inbox("--mark" in a)
    elif c == "all": cmd_sync(); cmd_site()
    else: print(__doc__)
main()
