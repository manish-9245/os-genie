#!/usr/bin/env python3
"""CLA step for os-genie-fix-pr. Run right after a PR is created.

Usage: cla_sign.py <upstream/repo> <pr-number> [--dry-run] [--wait 90]

Owner standing instruction (2026-10-16): if the CLA is signed by posting a PR
comment, post it immediately so the check is green before review; if the CLA is
signed any other way (web form, EasyCLA, PDF, line in the PR template), do NOT
sign: print a clear prompt for the owner with the link and exit 4.

How it decides: it reads the CLA bot's own comment on the PR. A bot comment that
says "sign the CLA by posting a Pull Request Comment" and quotes the phrase between
--- lines is comment-based (contributor-assistant/github-action). The exact quoted
phrase is posted, nothing else. Everything else is owner-action.
Exit: 0 signed or nothing needed, 4 owner action needed, 2 usage.
"""
import json, re, subprocess, sys, time

def gh(*a):
    return subprocess.run(["gh", *a], capture_output=True, text=True)

def main():
    if len(sys.argv) < 3: print(__doc__); sys.exit(2)
    repo, pr = sys.argv[1], sys.argv[2]
    dry = "--dry-run" in sys.argv
    wait = int(sys.argv[sys.argv.index("--wait") + 1]) if "--wait" in sys.argv else 90
    me = gh("api", "user", "--jq", ".login").stdout.strip()
    deadline = time.time() + wait
    seen = None
    while True:
        r = gh("api", f"repos/{repo}/issues/{pr}/comments", "--paginate")
        try: comments = json.loads(r.stdout or "[]")
        except Exception: comments = []
        for c in comments:
            b = c.get("body") or ""
            if re.search(r"(CLA|Contributor License Agreement)", b, re.I) and re.search(r"(sign|agree)", b, re.I) \
               and (c.get("user", {}).get("type") == "Bot" or c["user"]["login"].endswith("[bot]") or "github-actions" in c["user"]["login"]):
                seen = b; break
        if seen or time.time() > deadline: break
        time.sleep(10)
    if not seen:
        print("CLA: no CLA bot comment found yet (repo may not require one, or the bot is slow). Re-run later.")
        sys.exit(0)
    low = seen.lower()
    unsigned = re.search(r"(not[- ]signed|has not signed|have to sign|please sign|sign (our|the) (cla|contributor)|you can sign|before we can accept)", low)
    if not unsigned and re.search(r"(all contributors have signed|have signed the cla|cla signed|signed the cla)", low):
        print("CLA: already signed."); sys.exit(0)
    m = re.search(r"Pull Request Comment[^\n]*\n(?:\s*[-–—]+\s*(?:<br>)?\s*\n)?\s*(?:<br>)?\s*(.+?)\s*\n\s*[-–—]+", seen, re.S)
    if not m:
        m = re.search(r"\n\s*-\s*-\s*-\s*\n\s*(.+?)\s*\n\s*-\s*-\s*-", seen, re.S)
    if m:
        phrase = re.sub(r"<[^>]+>", "", m.group(1)).strip().splitlines()[0].strip()
        if me and any(c["user"]["login"] == me and c["body"].strip() == phrase for c in comments):
            print("CLA: signing comment already posted by you."); sys.exit(0)
        print(f"CLA: comment-based. Signing phrase: {phrase!r}")
        if dry: print("(dry run: not posting)"); sys.exit(0)
        out = gh("pr", "comment", pr, "--repo", repo, "--body", phrase)
        print("CLA: signing comment posted." if out.returncode == 0 else f"CLA: post failed: {out.stderr[:150]}")
        sys.exit(0 if out.returncode == 0 else 4)
    links = re.findall(r"https?://[^\s)>\"']+", seen)
    print(f"CLA ACTION NEEDED (owner): {repo}#{pr} requires a CLA that is not signed by comment.")
    for l in links[:3]: print("  sign here:", l)
    sys.exit(4)

main()
