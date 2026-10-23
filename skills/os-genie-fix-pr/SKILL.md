---
name: os-genie-fix-pr
description: Implement a GitHub issue fix and open a merge-ready pull request with tests, evidence, and docs. Use when asked to fix an issue, implement a contribution, create a PR, or turn a triaged issue into shippable code.
license: MIT
metadata:
  version: "1.2"
  pipeline-stage: "2-implement"
  prev-skill: os-genie-issue-triage
  next-skill: os-genie-maintainer-comms
---

# OSS Fix PR

**Ship the smallest green PR a maintainer can merge with confidence.**

## When to use

- User points at a triaged issue and asks to fix / implement / open a PR
- Any open-source code change destined for upstream review

## Preconditions (stop if unmet)

1. Issue scored >= 60 by `os-genie-issue-triage`, or user explicitly overrides with reason.
2. Policy recon passes per `references/policy-recon.md`: repo is GREEN or YELLOW, never RED. No-LLM repos are drops, not challenges.
3. `CONTRIBUTING.md` / `AGENTS.md` / PR template read. Repo PR template always wins over ours; every section gets filled. If none exists, fall back to `references/merge-checklist.md`.
4. No active assignee or green linked PR (re-check, state changes fast).

## Workflow

### 0. Policy recon first, code second

Run `references/policy-recon.md` before cloning: fetch AI policy +
CONTRIBUTING AI section + PR template, classify RED/YELLOW/GREEN.
RED means stop entirely. On YELLOW or human-submission-only repos, work
in safe mode: agent pushes the branch and writes the PR body to a file,
the human reviews (understanding check) and creates the PR. Authorship is the owner's:
PR text, commit messages and comments are written in the owner's plain voice
with no AI branding (no "AI-assisted" lines, no Claude/Anthropic trailers, no
"on behalf of"). Disclose only where the repo's own template, CONTRIBUTING or
AI policy asks for it, in the repo's own format and as briefly as it allows.
Never state anything untrue (no "tested locally" unless it was run). Never use
em dashes or en dashes in PR text, commits or comments.

### 1. Reproduce first, code second

- Set up per project docs; record exact setup commands for the PR's Testing section.
- Write or run a reproduction (script, failing test, or before/after screenshots for UI). No repro = no confidence claim.
- Polyglot pointers: Python `pytest <path> -x -q` / JS-TS `npm test -- <path>` / Go `go test ./<pkg>/` / Rust `cargo test <name>` / Java `./mvnw -pl <mod> test -Dtest=<Name>`. But project docs always win.

Completion criterion: failing behavior demonstrated before the fix, passing after.

### 2. Smallest focused diff: YAGNI

Data: PR size is the top velocity driver (LinearB 2025, 6.1M PRs): ~50 lines ideal, <200 good, <400 adequate, 400+ likely to miss issues. One concern per PR; no drive-by refactors.

Apply YAGNI (You Aren't Gonna Need It) to every hunk: implement only what the issue's acceptance criteria demand: nothing speculative, nothing "for later":

- No speculative generality: no extra config flags, option parameters, plugin hooks, or abstractions serving a single call site. Prefers duplication over the wrong abstraction; extract only on the second real use case.
- No future-proofing: no handling cases the issue doesn't report, no version-compat shims for unreleased versions, no TODO scaffolding for imagined follow-ups (file those as issue notes instead).
- No "while I'm here": adjacent dead code, renames, and formatting stay untouched unless they block the fix.
- Razor test per hunk: "Does the linked issue fail without this hunk?" If no, delete the hunk.

- Branch from updated `main`: `git checkout -b <type>/<short-slug>` (`fix/`, `feat/`, `docs/`). Never commit to `main`.
- Keep the diff under 200 lines changed where possible; over 400 requires splitting or explicit justification in the PR body.
- Follow Conventional Commits (`fix(scope): …`, `feat(scope): …`); reference the issue (`Fixes #123`). See `references/commit-guide.md`.

Completion criterion: every hunk passes the razor test, and the diff is the minimal change satisfying the acceptance criteria.

### 3. Tests + green CI are mandatory

Each additional failed CI check cuts merge odds ~15%; not-merged agentic PRs skew heavily to CI failures (AIDev/MSR 2026). Maintainers rarely merge untested code.

1. Add or update tests covering the fix (unit preferred; integration where the project demands it).
2. Run the project's full relevant suite + linter locally; paste commands + results.
3. Push and verify CI green via `gh pr checks`. Fix every red check before requesting review. Never ask a maintainer to review a red PR.

#### 3b. Trace the whole path, then prove every hunk (added after utopia#1380 lost to #1381)

utopia#1380 fixed 4 error sites, missed a 5th (the class lookup that also swallowed the error), and its test never reached 3 of its 4 hunks while the PR body claimed it did. A rival PR with the complete fix won. Three mandatory steps:

1. **Swallow-site audit (error-propagation and "X silently ignored" fixes).** Before editing, list every site between the entry point and the failing call that catches, logs-and-continues, `.ok()`s, defaults, or `unwrap_or`s the error (`grep -n "Err(\|\.ok()\|unwrap_or\|continue\|warn" <files on the path>`, then follow each callee one level down). Put the list in the evidence file as `SITES:` lines with covered/not-covered. A site you leave alone needs a one-line reason in the PR body.
2. **Make the test reach the code.** For each branch the test claims to exercise, assert it ran (a counter, a mock call count, an `embed_calls() > 0`). A fixture that cannot reach the branch (for example a threshold the fixture never crosses) must be fixed or the claim dropped.
3. **Per-hunk mutation check.** Commit the fix, then run `python3 scripts/hunk_check.py <upstream/base> <evidence> -- <focused test cmd>`. It reverts each source hunk alone and demands a test failure. `uncovered=0` is required by `check_evidence.py`; otherwise add a test, delete the hunk, or record `HUNK-WAIVER: file:line reason` and list it under "Not covered by tests" in the PR body.

The PR body may only claim coverage the hunk check proved. No "covers X" for an X without a failing-without-it test.

### 4. Evidence pack (screenshots where it matters)

- UI change: before/after screenshots or short clip, attached to the PR.
- Behavior/API change: repro script output or test run transcript.
- Perf claim: benchmark before/after with commands (no bare adjectives like "faster").
- Store large binaries out of git; attach via the PR UI unless the project requires otherwise.

### 5. Self-review + secrets sweep, then open the PR

Run `scripts/verify_pr.sh` (secrets scan, diff-size guard, branch guard). Then self-review your own diff line by line and remove: credentials, `.env`, debug prints, unrelated formatting, IDE configs, TODO planning files.

**Mandatory gate (numpy#33046 was closed because this was skipped).** Never write a
PR body from scratch. Print the repo's real template, fill EVERY section under its
own headings, add a disclosure only if the repo asks for one, and open the PR only through
the wrapper, which refuses on any mismatch:

```bash
python3 scripts/check_pr_body.py <upstream/repo> --show-template   # see the real template (also pass any body path)
# write /tmp/pr-body.md by filling that template, section by section
git push -u origin <type>/<short-slug>
bash scripts/open_pr.sh <upstream/repo> <fork-owner>:<branch> <base> "<type>(<scope>): <specific description>" /tmp/pr-body.md /tmp/evidence.md   # or: docs-only
gh pr checks --watch
```

`open_pr.sh` runs `check_evidence.py` (code needs local test evidence), then `check_pr_body.py`, then opens the PR and runs `cla_sign.py`. It blocks (exit 1) when a template
heading is missing, empty, or out of order; when the repo mentions AI but the body has
no disclosure; or when the agent ticked an attestation box ("I wrote this myself",
"without relying on an AI", "tested on a live environment"). It stops with exit 3
(HUMAN_SUBMIT) on repos whose template/CONTRIBUTING says interactions or PR submission
must be performed by humans (numpy). Never bypass it with a direct `gh pr create`.

On human-submission-only repos the agent stops after the push and hands
the human `/tmp/pr-<n>-body.md` plus the understanding check
(`references/policy-recon.md` section 5). The human creates the PR.

Completion criterion: PR is green, single-concern, templated, and linked to the issue, ready for `os-genie-maintainer-comms` follow-ups.

## Burst and testing rules (set 2026-10-18)

- **Org cap:** at most 2 PRs per upstream org per day. `open_pr.sh` runs `scripts/check_caps.py` and refuses the third. Ten PRs to freeCodeCamp in about an hour were each closed within 1 to 3 minutes, unread. Wait for a maintainer response before sending more to the same org. An override needs a stated reason in `OSG_CAP_OVERRIDE`.
- **Testing box:** when the repo's PR template has a testing checkbox ("I have tested these changes"), run the project's tests or docs build first, record evidence, and tick it. `check_pr_body.py` blocks a body that leaves it unticked. Never open a PR with that box unticked or with a note that tests were skipped. If the toolchain is missing, report SKIPPED and do not open the PR.

## Owner rules (non-negotiable, set 2026-10-16)

1. Follow the repo's PR template AND contribution guidelines exactly, every time. Read CONTRIBUTING, the template and any AI policy before cloning.
2. Write in the owner's plain voice. Say only what the template/guidelines need. Do not name the AI tool unless the repo asks (then one short line in its format). No em or en dashes and no semicolons in prose (only inside code).
3. Code work is always local: clone, fix, run the real tests, and keep evidence (`scripts/evidence.sh`: a failing BEFORE run with the fix reverted, a passing AFTER run). `scripts/open_pr.sh` refuses a code diff without it. No evidence, no PR. There is no "open as draft because untested" fallback: if the toolchain is missing, report SKIPPED. Docs-only diffs are exempt.
4. CLA: if the CLA bot is comment-based, post its exact signing phrase right after the PR opens (`scripts/cla_sign.py`, done by `open_pr.sh`) so the check is green before review. Any other CLA (web form, EasyCLA, PDF, line in the template) is never signed by the agent: it prints a clear prompt for the owner with the link.
5. If the repo requires human-written text or a human to submit (numpy, uutils, fd), stop. Prepare the branch and the facts; the owner writes and posts. This is the one exception to rule 2, because passing agent text off as human-written breaks that repo's rules.

## Review loop (run at the start of every session and after every task)

1. `python3 scripts/ledger.py all` then `python3 scripts/ledger.py inbox` (writes `~/oss-genie/inbox.md`). Also read `~/progress.md` and `~/oss-genie/notes.md` for context and open owner actions.
2. For every item, act by its tag:
   - **FIX** (changes requested, inline review comment, failing CI, merge conflict): work in the PR's local clone (re-clone the fork branch if it was deleted). Reproduce, change, re-run the tests and record new evidence with `scripts/evidence.sh`. Push to the PR's own branch (a rebase may need `--force-with-lease` on the fork branch only, never upstream). Keep commits and the PR text short and in the maintainers' requested style.
   - **REPLY** (a maintainer asked something): answer the question asked, briefly, in the owner's plain voice, naming what changed and the commit. No AI mention, no thanks-padding. Post it with `gh pr comment` only where the repo allows agent replies. On repos that want human-written replies (the inbox marks them) write the draft to `~/oss-genie/drafts/` for the owner to post.
   - **READ** (an acknowledgement, no action needed): note it and move on.
   - **OWNER** (CLA, human-written replies, attestations): leave it, it shows in "Needs you" on the site.
3. Merge blockers get the same treatment as reviews: conflicts rebase, red CI gets fixed or explained, a stale PR gets a short ping after 7 days of silence.
4. `python3 scripts/ledger.py note owner/repo#N "what was done"` for each action, then `ledger.py inbox --mark` so handled items stop showing, then `ledger.py all`.
5. After a PR is MERGED, run `ledger.py cleanup --apply` to delete only that PR's local clone.

## Notes, site and cleanup (owner rules)

- **Notes:** every PR is recorded in `~/oss-genie/ledger.json` and `~/oss-genie/notes.md` (clone path, evidence path, state changes, owner actions). `open_pr.sh` registers each PR automatically. Add context with `python3 scripts/ledger.py note owner/repo#123 "text"`. Run `ledger.py all` at the end of every task to refresh live state.
- **Local site:** `python3 scripts/ledger.py serve` shows the ledger at http://localhost:8787 (needs-you list first, then one filterable table of PRs). It is a local page only. Nothing is published.
- **Cleanup, merged only:** delete a project's local clone only after its PR is MERGED. `python3 scripts/ledger.py cleanup` lists what it would delete and `--apply` deletes, after re-checking the PR state live on GitHub. Open, draft and closed-unmerged PRs keep their clones, because the owner may still need to fix or reopen them.

## Claims (owner rule: track them)

Issues where the owner asked to work on them are tracked with `python3 scripts/ledger.py claims` (it is part of `ledger.py all`). It records each one as Assigned to me, Waiting for a reply, No answer for N days, Taken by someone else, PR sent, or Issue closed. Check the list in the review loop: a claim with no answer after 14 days gets one short follow-up from the owner (not the agent), a claim taken by someone else is dropped, and `ledger.py drop-claim owner/repo#N "reason"` retires a claim that no longer matters. The agent never posts a claim comment on its own. Claims follow `os-genie-issue-triage/references/claim-guide.md` (approval first, daily and per-org caps).

## Competitor recheck (added 2026-10-23)

`open_pr.sh` runs `check_competitors.py` immediately before opening: any other PR (open, or merged/closed within 14 days) that mentions the same `Fixes #N` blocks the open. Triage-time checks go stale in hours (utopia#1381 appeared 5 hours after #1380). If blocked, comment on the existing PR with what it misses instead of opening a rival. When a maintainer says "happy to take a PR", still finish the swallow-site audit first: a maintainer-invited issue attracts rivals quickly, and completeness decides who wins.

## Rules

- Never force-push to upstream; never commit secrets. Scan the staged diff for `api_key|password|secret|token` assignments before pushing.
- Draft PR early only to ask about approach; mark ready only when green.
- If the fix balloons past scope, stop and propose a follow-up PR instead of growing this one.

## References

- Policy recon + disclosure + human-post gate: `references/policy-recon.md`
- Evidence + CLA: `scripts/evidence.sh`, `scripts/check_evidence.py`, `scripts/cla_sign.py`
- PR-body gate (template fidelity, disclosure, attestation, human-submit): `scripts/check_pr_body.py`, `scripts/open_pr.sh`
- Checklist: `references/merge-checklist.md`
- Evidence rules: `references/evidence-guide.md`
- Commits: `references/commit-guide.md`
- Body template: `templates/pull-request.md`
