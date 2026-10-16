# Fast-merge playbook: significant repos, issues that merge in days

Goal: PRs that land in <7 days on projects people have heard of. Speed comes
from picking the right repo AND the right issue, then shipping a diff a
maintainer can approve in one read.

## 1. Pick repos by merge velocity, not stars

Run `os-genie-repo-finder/scripts/find_fast_repos.sh <lang> 3000`. Keep repos with:

- median outsider merge time <= 72h and >= 5 outsider merges in the last 60 closed PRs
- >= 3k stars (significant) and pushed < 14d ago
- no AI ban (see `os-genie-fix-pr/references/policy-recon.md`)

Rank by median hours ascending. A 5k-star repo that merges in a day beats a
50k-star repo that merges in a month.

## 2. Pre-screen EVERY issue before an agent touches it

```bash
scripts/prescreen.sh <owner/repo> <number>   # JSON verdict PASS|REJECT, read-only
```

It rejects: not open, assigned, open PR via timeline cross-ref or search,
non-maintainer claimant comment in last 45d, maintainer doubt language
("not sure we want", "lint rule", "wontfix"...), no approval signal, maintainer
silent >180d. Oct 2026 lesson: 4 of 5 agents dispatched from an unscreened list
found the issue already taken (rclone #7842, minikube #23724, loki #20673,
argo-cd #29335). Screening costs seconds; a wasted agent costs a wave.

Dispatch agents only on PASS. Re-run the screen immediately before opening the PR.

## 3. Prefer these issue shapes (fastest merges)

1. Docs where code already shows the answer (config table, flag list, wrong link)
2. One-line / one-function bug with a maintainer-written repro or a failing test
3. Missing test for already-fixed behavior
4. Error-message or help-text wording the maintainer already proposed
5. Dead code / unused dep removal the maintainer agreed to

Avoid: refactors, "migrate X to Y" (maintainers often disagree, loki), large
features, anything where the maintainer asked a question and nobody answered.

## 4. Discovery queries that surface un-crowded issues

```bash
# fresh, unassigned, maintainer-confirmed, no linked PR
gh search issues --label "good first issue" --state open --no-assignee \
  --updated ">$(date -v-30d +%F)" --language <lang> --sort updated --limit 50 \
  --json repository,number,title,commentsCount,url
# comment count <= 3 usually means no claimant pile-up
# docs-flavoured
gh search issues --label documentation --label "help wanted" --state open --no-assignee --limit 50
# maintainer invited a PR
gh search issues '"PR welcome" OR "happy to review"' --state open --no-assignee --limit 50
```

Then `prescreen.sh` each hit; keep PASS only.

## 5. Make the PR approvable in one read

- Diff <= 60 lines, one concern, tests that fail before / pass after
- Follow template, commit style, changelog rule (bat needs `#PR ... @user` line)
- Disclose AI assistance where the repo asks; NEVER attest human authorship or post
  replies for the owner (hyper, thanos, rust-analyzer, tauri require human comms)
- One PR per repo at a time; reply to review within 24h (owner does this)

## 6. Kill list (do not dispatch)

CLA not yet signed by owner (copperhead, openfga): sign first, or the PR sits red.
Repos that closed an AI PR without comment (cli/cli pattern) go on a 90-day pause.
