# Commit guide (state of the art)

Default to Conventional Commits 1.0.0 unless the repo's docs mandate otherwise. Adoption data justifies the default: in a 2025 sample of 381 JavaScript projects, 360 contained Conventional Commits messages and 198 were at 80 percent or more (Kong et al. 2025, via Wikipedia "Conventional Commits").

## Format

```
<type>[scope]: <description>

[optional body]

[optional footer(s)]
```

The spec mandates only `feat` and `fix`. Other types (`build`, `chore`, `ci`, `docs`, `style`, `refactor`, `perf`, `test`) follow the Angular/commitlint convention and carry no SemVer meaning on their own. Breaking changes append `!` (`feat(api)!: ...`) and describe the break in a `BREAKING CHANGE:` footer.

## The seven rules (Beams, adapted for Conventional Commits)

From Chris Beams' "How to Write a Git Commit Message", adjusted where the `type(scope):` prefix takes over:

1. Separate subject from body with a blank line. Tooling (changelog generators, `git log --oneline`, GitHub truncation past 72 chars) depends on it.
2. Aim the full subject line at 50 chars; treat 72 as the hard limit. The prefix eats budget, so keep the description tight.
3. Start the description lowercase (`fix(auth): resolve ...`, not `Fix`). The type prefix replaces Beams' capitalization rule; match the spec's own examples.
4. No trailing period on the subject.
5. Imperative mood in the description. Test: "If applied, this commit will ___" ("resolve", "add", "prevent"). Never past tense ("fixed", "added").
6. Wrap the body at 72 chars. Git never wraps for you.
7. Body explains what and why, not how. The diff already shows how. One hard-to-summarize commit usually means two commits; split it (same instinct as YAGNI: one logical change per commit, refactoring separate from behavior).

## Type disambiguation (the number one pain point)

ICSE 2025 (Zeng et al., "A First Look at Conventional Commits Classification") analyzed 194 GitHub issues and 100 Stack Overflow questions and found type confusion the most common problem developers hit with Conventional Commits. Use this table:

| Situation | Type | Example |
|---|---|---|
| Wrong behavior now correct (user-visible) | `fix` | `fix(auth): reject expired refresh tokens` |
| Same behavior, faster or leaner | `perf` | `perf(parser): memoize repeated lookups` |
| New capability | `feat` | `feat(cli): add --json output flag` |
| Restructure, zero behavior change | `refactor` | `refactor(auth): extract session store` |
| Behavior change that also speeds up | `fix`, note perf in body | `fix(cache): evict stale entries on write` |
| Tests only | `test` | `test(auth): cover concurrent refresh` |
| Docs only | `docs` | `docs(contributing): add Windows setup` |
| CI/config/build, no prod code | `ci` / `build` / `chore` | `ci: run tests on Python 3.13` |
| Undoing a prior commit | `revert` | `revert: feat(api): add verbose flag` + `Refs: <sha>` |

When two types fit, pick the user-facing effect and mention the other in the body.

## Footers (git trailer format)

`Token: value`, one per line after a blank line following the body:

- `Fixes #123` (closes the issue on merge) or `Refs #123` (related, partial work).
- `BREAKING CHANGE: <what breaks and migration path>` (required with `!`).
- `Co-authored-by: Name <email>` for pair/agent collaboration.
- `Signed-off-by: Name <email>` only where the project enforces DCO (Linux kernel, CNCF projects); skip elsewhere.

## Full example

```
fix(auth): resolve token refresh race condition

Concurrent refreshes issued duplicate tokens because nothing
serialized on the session. This serializes refresh on the
session lock; repeat requests now share one in-flight token.

Fixes #123
```

## Enforcement

Prefer repos that lint this (`commitlint` with `@commitlint/config-conventional`, ideally via husky/lint-staged). If the repo has no linting, self-check: subject shape, imperative test, 72-char cap, blank line, footer. Interactive helpers (`git cz` with commitizen) help when the shape is unfamiliar.

## Branch names

`<type>/<short-slug>`: `fix/null-pointer-auth`, `feat/dark-mode-toggle`, `docs/windows-setup`.
