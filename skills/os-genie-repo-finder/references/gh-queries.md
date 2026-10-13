# gh query recipes: os-genie-repo-finder

## Seed candidates

```bash
# GitHub native contribute pages
open https://github.com/<owner>/<repo>/contribute

# Curated aggregators (browse by language)
open https://goodfirstissue.dev
open https://up-for-grabs.net
open https://www.firsttimersonly.com

# Label search by language, freshest first
gh search issues --state open --label "good first issue" \
  --language "<language>" --sort updated --order desc --limit 30
gh search issues --state open --label "help wanted" \
  --language "<language>" --sort updated --order desc --limit 30
```

## Health snapshot per repo

```bash
gh api repos/<owner/repo> \
  --jq '{license: .license.spdx_id, pushed_at, open_issues, archived, default_branch}'
gh repo view <owner/repo> --json stargazerCount,pushedAt,hasWiki --jq .
gh label list --repo <owner/repo> --limit 50
ls CONTRIBUTING.md README.md 2>&1
gh workflow list --repo <owner/repo> 2>&1 | head -20
```

## Activity evidence (feeds the scorer)

```bash
# Commit momentum: last 30d vs prior 30d (weekly sampling beats daily)
gh api repos/<owner/repo>/commits --paginate -q '.[].commit.author.date' \
  | sort | uniq -c | tail -12

# Issue resolution + responsiveness
gh issue list --repo <owner/repo> --state all --limit 50 \
  --json state,createdAt,closedAt,comments > issues.json

# PR latency + merge rate
gh pr list --repo <owner/repo> --state all --limit 50 \
  --json state,createdAt,mergedAt,comments > prs.json

# Bus factor sketch: 90d commit share by author
git clone --filter=blob:none --shallow-since="90 days ago" \
  https://github.com/<owner>/<repo>.git /tmp/<repo>-bus
git -C /tmp/<repo>-bus shortlog -sne HEAD | head -15
```
