# Scoring rubric: os-genie-issue-triage

Total 100 points. Score each dimension, sum, recommend only on >= 60.

## 1. Maintainer approval: 35 pts

| Signal | Points |
|---|---|
| Maintainer/collaborator comment explicitly confirming, e.g. "confirmed", "good to go", "PR welcome", "accepted" | 35 |
| `triaged` / `confirmed` / `accepted` / `approved` label, or assigned milestone, no dissent | 25 |
| `help wanted` + recent maintainer reply (<30d) in thread | 18 |
| `good first issue` label only, no maintainer comment | 10 |
| No maintainer signal at all | 0 |

Evidence rule: copy the comment URL or label name into the report. "Approved" without a pointer scores 0.

Who counts as a maintainer: only comments whose `authorAssociation` is `OWNER`, `MEMBER` or `COLLABORATOR`. A "confirmed" or "go ahead" from `NONE` or `CONTRIBUTOR` is not approval, and `score_issue.py` ignores it. Re-check by hand before claiming: `gh issue view <n> --repo <o/r> --json comments --jq '.comments[]|[.author.login,.authorAssociation]|@tsv'`.

Why this weight: agentic-PR failure studies show incorrect-implementation and wrong-scope rejections cluster where no maintainer confirmed scope first (MSR 2026 failure taxonomy, n=600 annotated rejections). Approval is the single strongest merge predictor available before coding.

## 2. Scope clarity: 25 pts

| Signal | Points |
|---|---|
| Repro steps + expected vs actual + acceptance criteria or concrete file/area pointer | 25 |
| Repro steps XOR acceptance criteria (one present) | 15 |
| Clear bug/feature narrative, no repro, no criteria | 8 |
| One-liner / screenshot-only / "doesn't work" | 0 |

Bonus +5 (cap 25): issue names exact files, packages, or test commands.

## 3. Freshness / activity: 20 pts

| Signal | Points |
|---|---|
| Maintainer reply <30d, issue updated <60d | 20 |
| Activity 60-90d | 12 |
| Activity 90-180d with confirm label/milestone intact | 6 |
| Stale >180d, no re-confirmation | 0 |

Rationale: GoodFirstIssue maintainer guidance, recent commits, replies, and triage activity are how contributors trust review is still possible.

## 4. Low collision risk: 10 pts

- 10: no assignee, no linked PR, no "I'm working on it" comment <30d
- 4: stale claim (>30d silence from claimant), worth a polite "still working on this?" check
- 0: active assignee or open linked PR touched <14d → hard-reject, do not score further

## 5. Evidence quality: 10 pts

- 10: version/environment given + logs/stack trace or minimal repro
- 5: partial (version xor logs)
- 0: neither

## 6. Block-risk penalty: 0 to -20 (applied after the sum)

Subtract from the 0-100 total, floor at 0. This penalty exists because a
high-scoring issue you cannot touch scores zero in practice.

- -20: issue timeline shows org "blocked <user>" or "deleted a comment"
  events (2 or more), or the repo page states "Only collaborators can
  create PRs", or CONTRIBUTING forbids asking for assignment. Drop the
  issue regardless of the pre-penalty total.
- -10: zero maintainer approval combined with 5 or more "work on this?"
  comments, or an undecided maintainer question still open in thread.
  Treat as ask-first, never claim-first.
- 0: none of the above.

Worked penalty example: `pallets/flask#6146` (Oct 2026) looked small (one
docs link) but had zero approval, an open maintainer question, two prior
blocks with deletions on the same thread, and a collaborators-only PR gate.
Pre-penalty scope looked passable; post-penalty it is -20, hard drop. The
claim was posted anyway and the account was blocked with the comment
deleted.

## Worked example

`acme/widgets#412`: "panic on empty config", labelled `help wanted` + `confirmed`, maintainer comment 6d ago ("repro confirmed, PR welcome"), repro + expected/actual present, no assignee, version + stack trace included:

35 + 25 + 20 + 10 + 10 = **100** → strong recommend.

Same issue with no maintainer comment and only `good first issue` label: 10 + 25 + 6 + 10 + 10 = **61** → borderline; draft a scope-confirmation question first.
