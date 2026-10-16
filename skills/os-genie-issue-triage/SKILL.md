---
name: os-genie-issue-triage
description: Score and select quality, maintainer-approved GitHub issues worth fixing. Use when asked to find a good first issue, triage issues, vet an issue before coding, or decide which issue to work on.
license: MIT
metadata:
  version: "1.2"
  pipeline-stage: "1-triage"
  next-skill: os-genie-fix-pr
---

# OSS Issue Triage

**Pick issues a maintainer is likely to merge, not just issues labelled easy.**

## When to use

- User asks to find / pick / vet / triage a GitHub issue to fix
- Before any coding starts on an open-source issue
- To rank 3+ candidate issues and recommend exactly one

## Non-goal

Do not write code in this skill. Output is a ranked recommendation + claim comment draft. Coding belongs to `os-genie-fix-pr`.

## Workflow

### 1. Collect candidates (labels + text, not labels alone)

Only ~40% of repos have label-discoverable easy issues, so labels alone miss most good work (GitHub good-first-issues ML launch, 2020). Query both:

1. Label search first: `good first issue`, `help wanted`, `documentation`, plus repo synonyms (`beginner friendly`, `easy bug fix`, `low-hanging-fruit`, `good-first-issue`, `first-timers-only`). See `references/gh-queries.md`.
2. Text search for approval + scope signals: `maintainer replied`, `confirmed`, `triaged`, `accepted`, `milestone:*`, `reproducible`, `acceptance criteria`.
3. Gather 5-10 candidates max. For each, record: number, title, labels, age, assignees, comment count, last maintainer reply date, linked PRs, body length.

Stop when you have 5 candidates or 2 pages of search results, whichever comes first.

### 2. Hard-reject filter (any one = drop)

Run `scripts/prescreen.sh <owner/repo> <n>` on every candidate first; it automates
the checks below plus claimant and maintainer-doubt detection. Only PASS survives.
Agents must never be dispatched on an unscreened issue (see `references/fast-merge-playbook.md`).

- Labelled `wontfix`, `invalid`, `duplicate`, `needs-info` / `question` with no maintainer follow-up
- Already assigned, or has an open linked PR that is green/active (<14 days)
- No maintainer comment in >180 days AND no `triaged`/`confirmed`/`accepted` label
- Pure discussion / roadmap / RFC with no agreed scope ("we should maybe…", no decision comment)
- Open PR from anyone (timeline cross-reference or search), any claimant comment <45d, or maintainer doubt ("not sure we want", lint rule conflicts, "wontfix")
- Security report that asks for private disclosure (route to SECURITY.md instead, never triage publicly)

Completion criterion: every surviving candidate has zero hard-reject flags, stated explicitly.

### 3. Score survivors 0-100

Score each survivor with `references/scoring-rubric.md` (weights: maintainer approval 35, scope clarity 25, freshness/activity 20, low collision risk 10, evidence quality 10). You may use `scripts/score_issue.py` to compute it deterministically from `gh` JSON.

```bash
gh issue view <number> --repo <owner/repo> --json number,title,labels,assignees,comments,createdAt,updatedAt,body,state,milestone > issue.json
python3 scripts/score_issue.py issue.json
```

Completion criterion: every candidate has a numeric score with one-line justification per dimension.

### 4. Recommend exactly one

Pick the highest score. Tie-break: fresher maintainer reply wins, then smaller scope, then older issue age (stale-but-confirmed loses to fresh-and-confirmed).

Report:

1. Winner: `owner/repo#number` + title + score breakdown
2. Why it is mergeable: quote the maintainer approval signal (comment link or label)
3. Claim-comment draft per `references/claim-guide.md` (block-risk check + velocity caps + homework-first anatomy; scope question instead of a claim when approval is missing)
4. Runner-up + single reason it lost
5. Dropped candidates: one-line reject reason each

If no candidate scores >= 60, say so plainly and recommend asking a scope-clarifying question (via `os-genie-maintainer-comms`) instead of coding.

### 5. Block-risk + velocity gate (mandatory before posting anything)

Run `references/claim-guide.md` section 1 (four checks: approval, timeline,
contribution path, fresh collision) and section 2 (5/day global, 2/org,
60 min spacing, halve caps for new accounts). Any FAIL means do not post a
claim. Post a scope question or drop the issue. Never bypass this gate for
a "small docs fix": small scope does not waive approval, and the pallets
2026-10-14 block was a one-line docs claim with zero approval.

## Rules

- Pacing (freeCodeCamp 2026-10-16): at most 2 open PRs per repo from the account at a time. If 2 or more PRs in a repo are closed unmerged without a comment, STOP everything in that repo and tell the owner: it is a bulk-submission sweep and continuing risks an org block (pallets pattern). `prescreen.sh` enforces this.

- Quote maintainer approval; never assert "approved" without a comment, label, or milestone as evidence.
- Prefer issues with reproduction steps or acceptance criteria over vaguer higher-voted ones.
- Check duplicates before recommending: `gh search issues --repo <owner/repo> <keywords>`.
- Keep communication public on the issue; no DM asks.

## References

- Full rubric: `references/scoring-rubric.md`
- Claim guide (block-risk, velocity, human wording): `references/claim-guide.md`
- Fast-merge playbook (velocity picking, issue shapes, queries): `references/fast-merge-playbook.md`
- Search recipes: `references/gh-queries.md`
- Data sources: `references/evidence.md`
