---
name: os-genie-repo-finder
description: Find quality open-source repos where a first contribution is likely to get merged. Use when asked to find repos to contribute to, evaluate a repo before investing, build a contribution shortlist, or check merge chances.
license: MIT
metadata:
  version: "1.1"
  pipeline-stage: "0-discover"
  next-skill: os-genie-issue-triage
---

# OSS Repo Finder

**Contribute where maintainers still merge.**

## When to use

- User asks "where should I contribute?" / "find repos" / "is this repo worth it?"
- Before running `os-genie-issue-triage` on an unfamiliar repo
- To build or re-rank a shortlist of 3-5 candidate repos

## Workflow

### 1. Fix the search frame

Ask (or assume + state): languages, domain interests, max setup tolerance, goal (one merged PR vs long-term relationship). Default frame if unstated: user's known languages, docs/tests/bug-fix scope, setup <30 min.

Sources to seed candidates: `github.com/<owner>/<repo>/contribute`, goodfirstissue.dev, up-for-grabs.net, firsttimersonly.com, GitHub search `label:"good first issue" language:<lang>`. See `references/gh-queries.md`.

Gather 5-8 candidates. Then score: never recommend unscored.

### 2. Hard-reject filter (any one = drop)

- No OSI-approved license (check `LICENSE` / `gh api repos/<o>/<r> --jq .license.spdx_id`)
- No commits on default branch in >90 days AND no maintainer replies in >60 days (dead or archived-adjacent)
- Open PRs rotting: median open-PR age >60d with no maintainer comment
- CONTRIBUTING missing AND README setup insufficient to build (<30 min attempt fails)
- Single-maintainer bottleneck with bus factor 1 + no merges in 60d
- Contribution friction: issue threads show org "blocked <user>" or deleted
  comments, the repo page gates PRs ("Only collaborators can create PRs"),
  or CONTRIBUTING forbids asking for assignment (pallets/flask#6146 pattern,
  Oct 2026: prior blocks plus a closed PR path made every claim unmergeable)
- AI-output ban: repo policy forbids LLM/AI-assisted contributions outright
  ("No LLMs", no AI-assisted PRs — torchgeo/.github/AI_POLICY.md pattern,
  Oct 2026: PR closed on sight). Disclosure-requiring repos (numpy-style)
  pass, but note the disclosure + human-submission cost in the score.

Completion criterion: every survivor passes all six, stated explicitly.

### 3. Score survivors 0-100

Use `references/health-rubric.md` (weights: momentum 30, bus factor 25, issue health 20, PR latency 15, release cadence 10, adapted from `gh-analyzer` with LFX/CHAOSS/CSI rationale). Deterministic option:

```bash
gh api repos/<owner/repo> --jq '{pushed_at, open_issues, license}'
gh issue list --repo <owner/repo> --state all --limit 50 --json state,createdAt,closedAt > issues.json
gh pr list --repo <owner/repo> --state all --limit 50 --json state,createdAt,mergedAt > prs.json
python3 scripts/score_repo.py --repo <owner/repo> --issues issues.json --prs prs.json
```

Prefer medians over means for resolution/latency (outliers lie, CSI validation, Adejumo & Johnson 2025). Completion criterion: every candidate scored with per-dimension evidence.

### 4. Recommend a shortlist

Report top 3 with: score breakdown, license + CONTRIBUTING + CI status, last-commit / last-merge / median-first-response facts, 1-2 linked beginner-friendly issues each, and setup-time estimate. Name one first-pick repo + the issue to triage next via `os-genie-issue-triage`.

If nothing scores >= 60, say so and widen the frame (adjacent language, larger org, docs-first repos) rather than forcing a bad pick.

## Rules

- Verify merge behavior from data (recent merges, closed issues, review comments), never from stars alone.
- Favor repos you actually use; "showing up" cold has the worst hit rate (maintainer wisdom, opensource.guide).
- Quality over quantity: one thoughtful merged PR beats ten trivial ones.

## References

- Rubric: `references/health-rubric.md`
- Queries: `references/gh-queries.md`
- Data sources: `references/evidence.md`
