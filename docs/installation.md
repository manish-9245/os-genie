# Installation

## One-line install (recommended)

```bash
npx skills add manish-9245/os-genie
```

The CLI detects your installed agents (Claude Code, Cursor, OpenCode, Codex, and 70+ more) and installs all four OS Genie skills into each one. Requires Node.js 18+.

List what was found in the repo without installing:

```bash
npx skills add manish-9245/os-genie --list
```

Install a single skill to specific agents:

```bash
npx skills add manish-9245/os-genie --skill os-genie-fix-pr -a claude-code -a opencode
```

## Manual install

Portable Agent Skills work anywhere by copying folders. Pick one scope:

```bash
# Per-project: commit so the whole team gets them (Claude Code shown)
cp -r skills/os-genie-* /path/to/project/.claude/skills/

# Personal: all your projects on this machine
mkdir -p ~/.claude/skills && cp -r skills/os-genie-* ~/.claude/skills/
```

Other hosts use the same shape under different roots (`.agents/skills/`, `.cursor/skills/`, `.codex/skills/`). The `npx skills add` command handles those paths for you.

## Verify the install

```bash
# Frontmatter + spec validation (needs npm)
npx -y skills-ref validate ./skills/os-genie-repo-finder
npx -y skills-ref validate ./skills/os-genie-issue-triage
npx -y skills-ref validate ./skills/os-genie-fix-pr
npx -y skills-ref validate ./skills/os-genie-maintainer-comms

# Scorer smoke tests (needs python3, stdlib only)
echo '{"number":1,"title":"t","labels":[{"name":"help wanted"},{"name":"confirmed"}],"assignees":[],"comments":[{"body":"repro confirmed, PR welcome"}],"createdAt":"2026-09-01T00:00:00Z","updatedAt":"2026-10-10T00:00:00Z","body":"Steps to reproduce: run. Expected X. Actual Y in src/a.py. Version 2.1, stack trace included."},"state":"OPEN","milestone":null}' \
  | python3 skills/os-genie-issue-triage/scripts/score_issue.py /dev/stdin
# → verdict RECOMMEND

# Pre-PR gate syntax (needs bash + git)
bash -n skills/os-genie-fix-pr/scripts/verify_pr.sh && echo GATE-SYNTAX-OK
```

## Prerequisites for live use

| Tool | Needed for | Check |
|---|---|---|
| `gh` (authed) | All live repo/issue/PR queries | `gh auth status` (login: `gh auth login`) |
| `git` | Branching, diffing, PR workflow | `git --version` |
| `python3` | Both scorers | `python3 --version` (stdlib only, no deps) |
| `bash` | `verify_pr.sh` | present on macOS/Linux by default |

No API keys, no daemons, no build step. Everything runs offline on saved `gh` JSON if you prefer (see [pipeline](pipeline.md)).

## Updating and uninstalling

```bash
npx skills update os-genie-repo-finder   # single skill
npx skills update                        # everything (interactive scope prompt)
npx skills remove os-genie-fix-pr        # or `rm` alias
```

Manual installs update by re-copying the folders.

## Troubleshooting

- **`gh` prompts for auth**: run `gh auth login` and pick HTTPS with your account.
- **Validator complains about frontmatter**: OS Genie uses strict portable frontmatter (`name`, `description`, `license`, `metadata` only). File an issue if validation fails on a clean checkout.
- **Scorer exits non-zero**: that is by design. Exit 0 means RECOMMEND, exit 2 means ASK-FIRST/SKIP with reasons in the JSON. Read the breakdown before overriding.
- **`verify_pr.sh` blocks**: it fails loudly on purpose (main-branch commits, secret patterns, >400-line diffs, red CI). Fix the flagged lines, do not bypass.
