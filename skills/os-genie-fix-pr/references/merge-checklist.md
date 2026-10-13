# Merge checklist: os-genie-fix-pr

Every box must be checked before requesting review. Designed so a maintainer can merge on first read.

## Scope (YAGNI)

- [ ] Single concern; linked issue quoted (`Fixes #123`)
- [ ] Diff <200 lines changed preferred; <400 max without written justification
- [ ] No unrelated refactors, formatting sweeps, or scope creep (split follow-ups instead)
- [ ] YAGNI: no speculative flags/options/hooks, no future-proofing, no "while I'm here" cleanups
- [ ] Every hunk passes the razor test: the linked issue fails without it

## Correctness

- [ ] Repro demonstrated failing-before / passing-after
- [ ] New or updated tests cover the fix; existing suite green locally
- [ ] Linter/formatter per project config passes

## CI & hygiene

- [ ] `gh pr checks` all green (each extra failed check cuts merge odds ~15%, AIDev/MSR 2026)
- [ ] Branch is `type/slug` off updated `main`; PR targets correct base branch (wrong-branch is a known agentic rejection pattern)
- [ ] Conventional Commit title, specific (not "Fixed bug" but "fix(auth): resolve token refresh race")
- [ ] Secrets sweep clean: no `.env`, keys, tokens, debug prints, IDE configs, planning files

## PR body (see templates/pull-request.md)

- [ ] Summary: what + why in 3 lines
- [ ] Changes: bullet list of code changes
- [ ] Related issues: `Fixes #123`
- [ ] Testing: exact commands + results (copy-pasteable)
- [ ] Evidence: screenshots/transcripts/benchmarks attached where applicable
- [ ] Notes: follow-ups or deliberate non-goals stated

## Self-review

- [ ] Read own diff top to bottom; every hunk justified
- [ ] PR template of the repo used if one exists (repo template beats ours)
- [ ] Description is meaningful: empty/vague descriptions are an annotated rejection pattern
