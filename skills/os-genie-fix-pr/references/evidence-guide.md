# Evidence guide: os-genie-fix-pr

Match evidence to change type. Claims without artifacts read as noise to reviewers.

## UI / visual change (mandatory screenshots)

1. Capture before screenshot (current `main`, same viewport/data).
2. Capture after screenshot (your branch, same viewport/data).
3. Attach both to the PR with one-line captions of what changed.
4. For interactions, a <30s clip beats 5 screenshots.

Name files `before-<slug>.png` / `after-<slug>.png`. Do not commit them to git unless the project requires it, attach via PR UI.

## Behavior / API change

- Repro script + output transcript (failing before, passing after).
- Test run transcript: exact command + pass count, e.g. `pytest tests/auth -q → 14 passed`.
- For error-path fixes: include the exact error string before and its absence after.

## Performance change

- Benchmark command, environment (CPU/RAM or runner), N runs, before/after numbers with units.
- Never claim "faster" without numbers. Small diffs with numbers merge; big claims without them don't.

## Docs / config-only change

- Rendered preview or `diff` excerpt showing the resolved output.
- Link to passing docs build / lint if CI provides one.

## What not to attach

Secrets, `.env` contents, full local logs with tokens, multi-MB binaries in git. Redact tokens as `***` before pasting any log.
