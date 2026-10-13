# Health rubric: os-genie-repo-finder

Total 100. Recommend on >= 60; first-pick should be >= 75. Weights adapted from `gh-analyzer` (momentum 30 / bus 25 / issue-health 20 / PR-latency 15 / release 10), rationale from LFX Insights, CHAOSS, and the Composite Stability Index (CSI).

## 1. Commit momentum: 30 pts

Compare last-30d commits vs prior-30d (weekly sampling; daily is too bursty for most repos, CSI validation).

| Signal | Points |
|---|---|
| Growing or steady (±20%), commits in last 14d | 30 |
| Mild dip (−20 to −50%), still active | 18 |
| Severe drop (>−50%) or nothing in 30d | 5 |
| Nothing in 90d | 0 (= consider hard-reject) |

## 2. Bus factor / maintainer coverage: 25 pts

Bus factor = # contributors whose removal loses >50% of knowledge (truck-factor algorithm); HHI concentration as tiebreak.

| Signal | Points |
|---|---|
| ≥3 active mergers + no single author >50% of 90d commits | 25 |
| 2 active mergers, top author 50-70% | 15 |
| Bus factor 1 (single person merges everything) | 5 |
| No merges in 60d regardless of headcount | 0 |

LFX reference: healthy projects show multiple maintainers with merge rights + org diversity; 25 merge-rights holders is their exemplar, not the bar. 2-3 suffices for contributor purposes.

## 3. Issue health: 20 pts

Resolution rate on last-50 issues + median time-to-first-maintainer-response (median, not mean).

| Signal | Points |
|---|---|
| ≥70% closed + median first response ≤14d | 20 |
| 50-70% closed XOR response ≤30d | 12 |
| <50% closed and response >30d | 4 |
| Issues unanswered >60d piling up | 0 |

## 4. PR latency: 15 pts

Median open→merge on last-20 merged PRs.

| Signal | Points |
|---|---|
| Median ≤7d | 15 |
| 7-21d | 10 |
| 21-60d | 5 |
| >60d or merge rate <30% of opened | 0 |

Merge-rate context: healthy OSS merges a steady share; agentic-PR era data shows docs/CI/build merge highest (74-84%). Repos with green CI + test docs merge faster (TER correlations ρ≈0.34-0.36).

## 5. Release cadence / contributor loop: 10 pts

| Signal | Points |
|---|---|
| Release or meaningful tag in ≤90d + CONTRIBUTING + CI + runnable tests | 10 |
| Two of (recent release, CONTRIBUTING, CI) | 6 |
| One or none | 0 |

GoodFirstIssue maintainer bar (must all hold for the +): public, active, README + CONTRIBUTING + license + setup/test instructions clear enough for a newcomer.

## Worked example

`acme/widgets`: steady commits (30), 4 mergers top-38% (25), 80% issues closed median response 6d (20), median merge 3d (15), release 20d ago + CONTRIBUTING + CI (10) = **100**.

Same repo with bus factor 1 and 45d median merge: 30 + 5 + 20 + 5 + 10 = **70** → still recommendable, but flag single-maintainer risk.
