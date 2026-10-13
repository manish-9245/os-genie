# Evidence: why this triage works

Data backing the weights and filters in `os-genie-issue-triage`. Summaries only; consult originals before quoting numbers publicly.

1. **Labels are necessary but insufficient.** GitHub's good-first-issues launch (Gazit, GitHub Blog, Jan 2020): initial label-based recommendations covered only ~40% of recommended repos; team added ML text-based detection and ranked label matches above ML matches with an age penalty. Takeaway: search labels AND text, penalize stale issues. Source: `github.blog/open-source/maintainers/how-we-built-good-first-issues`.
2. **Newcomer barriers are real and labelled issues help only when scoped.** Tan et al., "A First Look at Good First Issues on GitHub", ESEC/FSE 2020 (cited 100+ times): GFI mechanism aids onboarding, but newcomers still struggle to locate suitable tasks; issue quality (context, criteria) matters more than label presence.
3. **Scope confirmation prevents the top agentic failure modes.** "Where Do AI Coding Agents Fail?", arXiv Jan 2026 (33,596 agentic PRs; 600 manually annotated rejections): rejection patterns include CI/test failure (99), incorrect implementation (19), non-functional PRs (2%), wrong task descriptions (1%), wrong branch. A confirmed scope + repro before coding directly attacks incorrect-implementation and wrong-description rejections.
4. **Maintainer responsiveness predicts review.** GoodFirstIssue.org maintainer guide + LFX Insights health model: recent commits, replies, and triage activity signal that review is still possible; median response time and issue-resolution rate are first-class health signals. Stale-without-confirmation issues are the highest abandonment risk.
5. **Small, reviewable scope wins.** LinearB 2025 Benchmarks (6.1M PRs, 3,000 teams): PR size is the most significant driver of velocity; ~50 lines ideal, <200 good, <400 adequate, 400+ likely to miss issues. Prefer issues whose fix plausibly fits <200 lines.

## Method note

Weights (approval 35 / clarity 25 / freshness 20 / collision 10 / evidence 10) are a practitioner synthesis of the above, not a fitted model. The 60-point recommend threshold is a guardrail: below it, ask a clarifying question (see `os-genie-maintainer-comms`) instead of coding.
