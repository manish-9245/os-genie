# Pipeline walkthrough

The four skills form one chain. Work it in order; each stage gates the next.

```
os-genie-repo-finder → os-genie-issue-triage → os-genie-fix-pr → os-genie-maintainer-comms
```

## Stage 0: Discover (os-genie-repo-finder)

Goal: 3 scored repos, one first-pick. State your frame first (languages, domain, setup tolerance), seed candidates from `github.com/<o>/<r>/contribute`, goodfirstissue.dev, up-for-grabs.net, or `label:"good first issue" language:<lang>` search, then score.

```bash
gh api repos/acme/widgets --jq '{license: .license.spdx_id, pushed_at, open_issues}'
gh issue list --repo acme/widgets --state all --limit 50 \
  --json state,createdAt,closedAt > issues.json
gh pr list --repo acme/widgets --state all --limit 50 \
  --json state,createdAt,mergedAt > prs.json
python3 skills/os-genie-repo-finder/scripts/score_repo.py --repo acme/widgets \
  --issues issues.json --prs prs.json \
  --commits-30d 40 --commits-prior-30d 38 --mergers 4 --top-share 0.38 \
  --released-days-ago 20 --docs 3
```

Worked result: `{"score": 92, "verdict": "FIRST-PICK"}`. Below 60 means SKIP: widen the frame (adjacent language, larger org, docs-first repos) instead of forcing a bad pick. Hard-rejects (no OSI license, dead 90d, rotting PRs, unbuildable setup, bus-factor-1 with no merges) drop a repo before scoring.

## Stage 1: Triage (os-genie-issue-triage)

Goal: exactly ONE issue with quoted maintainer approval. Never code first.

```bash
gh issue list --repo acme/widgets --state open --label "help wanted" --limit 30
gh issue view 412 --repo acme/widgets \
  --json number,title,labels,assignees,comments,createdAt,updatedAt,body,state,milestone > issue.json
python3 skills/os-genie-issue-triage/scripts/score_issue.py issue.json
```

Worked result for `acme/widgets#412` ("panic on empty config", `confirmed` label, maintainer "repro confirmed, PR welcome" 6 days ago, repro plus expected/actual, version plus stack trace):

```
approval 35 + clarity 25 + freshness 20 + collision 10 + evidence 10 = 100 → RECOMMEND
```

Output is the winner, its score breakdown, a claim-comment draft, the runner-up with its losing reason, and one-line reject reasons for the rest. Below 60 means ASK-FIRST: draft a scope question with os-genie-maintainer-comms Template A instead of coding.

## Stage 2: Implement (os-genie-fix-pr)

Goal: the smallest green PR a maintainer can merge on first read.

1. Reproduce first: failing behavior demonstrated before the fix, passing after. No repro means no confidence claim.
2. YAGNI diff: every hunk must pass "does the linked issue fail without this hunk?" No speculative flags, no future-proofing, no drive-by cleanups. Under 200 lines; over 400 gets split.
3. Tests plus green CI: add or update tests, run the suite and linter locally, push, then `gh pr checks` until all green. Never request review on red.
4. Evidence pack: before/after screenshots for UI, transcripts for behavior, numbers (never adjectives) for perf.
5. Gate and ship:

```bash
git checkout -b fix/empty-config-panic
# ... edits ...
bash skills/os-genie-fix-pr/scripts/verify_pr.sh   # secrets, size, branch guards
git push -u origin fix/empty-config-panic
gh pr create --title "fix(config): reject empty config with actionable error" \
  --body-file skills/os-genie-fix-pr/templates/pull-request.md
gh pr checks --watch
```

Commits follow the state-of-the-art guide (`references/commit-guide.md`): Conventional Commits, imperative mood, 50-char aim with 72 hard cap, what-and-why body, `Fixes #412` trailer.

## Stage 3: Communicate (os-genie-maintainer-comms)

Goal: every reply easy to say yes to.

- Classify first: scope doubt (Template A), agree (B), clarify (C), disagree with data and deference (D), big-ask split proposal (E), 7-day bump (F), graceful close (G).
- Address every comment 1:1 with commit hashes, push fixes to the same branch, re-run green, explicitly re-request review.
- Your SLA is 48h on actionable feedback; their silence gets one bump per 7 days, max two, then you log the repo as unresponsive (which feeds future Stage 0 scoring).

## The loop

Merged results flow back: record response time, templates used, and merge outcome per repo. That history makes the next Stage 0 shortlist sharper than any static search.
