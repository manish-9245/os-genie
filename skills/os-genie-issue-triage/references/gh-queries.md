# gh query recipes: os-genie-issue-triage

All commands need `gh` authenticated (`gh auth login`). Replace `<owner/repo>` and `<language>`.

## Candidate discovery

```bash
# Label-based: beginner-friendly pool in one repo
gh issue list --repo <owner/repo> --state open \
  --label "good first issue" --limit 30
gh issue list --repo <owner/repo> --state open \
  --label "help wanted" --limit 30

# Label synonyms worth trying per repo (list labels first)
gh label list --repo <owner/repo> --limit 50
# try: "beginner friendly", "easy bug fix", "low-hanging-fruit",
#      "good-first-issue", "first-timers-only", "documentation"

# Cross-repo discovery by language
gh search issues --state open --label "good first issue" \
  --language "<language>" --sort updated --order desc --limit 30

# Approval-signal search inside a repo
gh search issues --repo <owner/repo> --state open \
  "commenter:<maintainer-handle>" --sort updated --limit 20
```

## Per-issue inspection (feeds the scorer)

```bash
gh issue view <number> --repo <owner/repo> \
  --json number,title,labels,assignees,comments,createdAt,updatedAt,body,state,milestone
```

Checklist on the JSON: assignees empty? linked PRs in timeline? last maintainer comment date? milestone set? body has repro + expected/actual?

## Duplicate / collision check

```bash
# Duplicate scope
gh search issues --repo <owner/repo> --state all "<distinctive keywords>" --limit 10

# Open PRs referencing the issue number
gh search prs --repo <owner/repo> --state open "<issue-number>" --limit 10
gh pr list --repo <owner/repo> --state open --limit 30
```

## Freshness check

```bash
gh issue view <number> --repo <owner/repo> --comments | tail -30
gh api repos/<owner/repo> --jq '{pushed_at, open_issues}'
```
