---
name: os-genie-fix-pr
description: Implement a GitHub issue fix and open a merge-ready pull request with tests, evidence, and docs. Use when asked to fix an issue, implement a contribution, create a PR, or turn a triaged issue into shippable code.
license: MIT
metadata:
  version: "1.1"
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
the human reviews (understanding check) and creates the PR. Disclosure is
mandatory everywhere a policy asks for it, and honest everywhere else.

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

### 4. Evidence pack (screenshots where it matters)

- UI change: before/after screenshots or short clip, attached to the PR.
- Behavior/API change: repro script output or test run transcript.
- Perf claim: benchmark before/after with commands (no bare adjectives like "faster").
- Store large binaries out of git; attach via the PR UI unless the project requires otherwise.

### 5. Self-review + secrets sweep, then open the PR

Run `scripts/verify_pr.sh` (secrets scan, diff-size guard, branch guard). Then self-review your own diff line by line and remove: credentials, `.env`, debug prints, unrelated formatting, IDE configs, TODO planning files.

Open with `templates/pull-request.md` (or the repo's own template, which
always wins — fill every section, never leave template comments unfilled):

```bash
git push -u origin <type>/<short-slug>
gh pr create --title "<type>(<scope>): <specific description>" --body-file templates/pr-body.md
gh pr checks --watch
```

On human-submission-only repos the agent stops after the push and hands
the human `/tmp/pr-<n>-body.md` plus the understanding check
(`references/policy-recon.md` section 5). The human creates the PR.

Completion criterion: PR is green, single-concern, templated, and linked to the issue, ready for `os-genie-maintainer-comms` follow-ups.

## Rules

- Never force-push to upstream; never commit secrets. Scan the staged diff for `api_key|password|secret|token` assignments before pushing.
- Draft PR early only to ask about approach; mark ready only when green.
- If the fix balloons past scope, stop and propose a follow-up PR instead of growing this one.

## References

- Policy recon + disclosure + human-post gate: `references/policy-recon.md`
- Checklist: `references/merge-checklist.md`
- Evidence rules: `references/evidence-guide.md`
- Commits: `references/commit-guide.md`
- Body template: `templates/pull-request.md`
