# Methodology: why the numbers

Every gate in OS Genie traces to published data or validated tooling. Summaries below; consult the originals before quoting numbers publicly. Per-skill sources live in each skill's `references/evidence.md`.

## PR size drives velocity

LinearB 2025 Software Engineering Benchmarks (6.1M+ PRs, 3,000 teams): PR size is the most significant driver of engineering velocity. Small PRs review faster, merge safer, and shorten cycle time. Working bands used across the skills: ~50 lines ideal, <200 good, <400 adequate, 400+ likely to miss issues. Sources: LinearB 2025 Benchmarks Report and "PR Size Matters" (bssw.io). Drives: the <200-line rule, YAGNI razor test, Template E follow-up splits.

## Green CI drives merges

Empirical study of failed agentic PRs (33,596 PRs, 600 manually annotated rejections, arXiv Jan 2026): CI/test failure is the top rejection pattern (99 of 600); each additional failed CI check cuts merge odds about 15% (Cliff's delta 24%, moderate effect). The companion AIDev study (~933k PRs) adds: docs/CI/build tasks merge at 74 to 84% while feature/test/performance merge lower, and test-containing PRs trend larger and slower. Drives: never-request-review-on-red, mandatory tests, docs/CI-friendly scope preference.

## Maintainer approval drives scope correctness

Same failure taxonomy: incorrect implementation (19), wrong task descriptions (1%), non-functional PRs (2%), wrong branch. These cluster where scope was never maintainer-confirmed. GitHub's own good-first-issues launch (Gazit, 2020) shows labels alone cover only ~40% of repos, so text signals matter; Tan et al. (ESEC/FSE 2020) show issue quality beats label presence for newcomer success. Drives: 35 of 100 triage points on quoted approval, hard-reject on stale-unconfirmed issues, Template A scope questions.

## Repo health drives follow-through

Weights mirror `gh-analyzer` (momentum 30, bus factor via HHI 25, issue resolution 20, PR latency 15, release cadence 10). Rationale from LFX Insights (maintainer health, merge-rights holders, org diversity, median response), CHAOSS community health metrics, and the Composite Stability Index validation (Adejumo and Johnson, arXiv Aug 2025: weekly sampling beats daily for bursty repos; medians beat means for resolution times). Contributor-loop quality per GoodFirstIssue.org (active maintenance, clear writing, small scope, runnable tests plus responsive feedback). Testing-culture data: test engagement ratio mean 0.37, with how-to-run/write-tests docs correlating around 0.34 to 0.36 (160-repo OSS documentation study, 2025 to 2026). Drives: the five-dimension rubric, median-based scorer, CONTRIBUTING-plus-CI release-loop dimension.

## Commit quality

Conventional Commits 1.0.0 (type/scope/!/body/trailers); Beams' seven rules adapted for the prefix era; type-confusion guidance from ICSE 2025 (Zeng et al.: CCS-type confusion is developers' most common problem, from 194 GitHub issues and 100 Stack Overflow questions); adoption context (Kong et al. 2025: 360 of 381 sampled JS projects contain CC commits). Full detail: `skills/os-genie-fix-pr/references/commit-guide.md`.

## Honesty note

The point weights (35/25/20/10/10, 30/25/20/15/10) and the 60/75 thresholds are practitioner syntheses of the above, not fitted models. They are guardrails with stated evidence, tuned to err toward asking before coding.
