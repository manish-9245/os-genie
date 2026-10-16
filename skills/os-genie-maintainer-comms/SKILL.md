---
name: os-genie-maintainer-comms
description: Draft maintainer replies, scope questions, review responses, and follow-up fixes. Use when a maintainer commented on your issue or PR, you need to ask a doubt, address review feedback, bump a stale thread, or propose a follow-up.
license: MIT
metadata:
  version: "1.1"
  pipeline-stage: "3-communicate"
  prev-skill: os-genie-fix-pr
---

# OSS Maintainer Comms

**Make every reply easy to say yes to.**

## When to use

- Maintainer asked a question, requested changes, or went silent
- You have a doubt blocking the fix and need to ask scope
- Review feedback arrived and needs addressing + re-review request
- A PR needs a polite bump or a follow-up split

## Principles (maintainer reality first)

Maintainers face overwhelm, volunteer time, and burnout; they protect the codebase through quality gates (opensource.guide; see `references/tone-rules.md`). So: public, concise, homework-done, patient.

- Public beats private: keep it on the issue/PR for future contributors.
- Concise beats complete: 3-8 lines, then evidence link. Maintainers skim.
- Homework first: search issues/PRs/docs, then ask with what you already tried.
- Patient: 7 days before a first bump, 48h response SLA on your side for review feedback.

## Workflow

### 1. Classify the incoming message

| Type | Move |
|---|---|
| Scope doubt you must ask | Template A: question with options + recommendation |
| Review: agree | Fix, cite commit, reply per-comment (Template B) |
| Review: need clarification | Template C: restate understanding, ask binary question |
| Review: disagree | Template D: reasons + data, defer to maintainer, offer alternative |
| Review: big ask / scope growth | Template E: propose follow-up PR split |
| Silence ≥7d, CI green, reviewable | Template F: single polite bump with status |
| Silence ≥21d or explicit wontfix | Template G: thank, close, log, do not argue |
| First contact, approval quoted, block-risk passed | Template H: homework-first claim ending in a question |
| No approval yet or block-risk soft-fail | Template I: scope question, never a claim |

Full templates: `references/response-templates.md`. First-contact wording
rules (banned openers, no sentence reuse, artifact required): `references/tone-rules.md`
plus triage `references/claim-guide.md` velocity caps.

### 2. Draft the reply

Rules: address every comment (no silent skips); quote or link each point; state what changed + commit hash; never argue tone, assume good intent; no AI filler ("Hope you're doing well!", "As an AI").

Human-post rule (non-negotiable on numpy/shapely-family repos, recommended
everywhere): the agent DRAFTS, the human POSTS. Several projects forbid
agents posting comments on an author's behalf and require all reviewer
interaction to be human. Never post a reply to GitHub without the human
reading it first. Drafts live in the session for approval, not straight to
`gh`.

Completion criterion: draft covers all reviewer points 1:1 and ends with an explicit ask (re-review / decision / confirmation).

### 3. Execute follow-up fixes via os-genie-fix-pr

- Push fix commits to the same branch; never open a second PR for review feedback.
- Re-run tests + `gh pr checks`; paste results into the reply.
- Re-request review explicitly: `gh pr ready` if draft, then comment "Ready for re-review, all green."
- If feedback grows scope past ~200 new lines, propose the split (Template E) and implement only after maintainer agrees.

### 4. Track and close the loop

- Unanswered after 7d → one bump (Template F). After 21d → close gracefully, note repo responsiveness for `os-genie-repo-finder` scoring.
- Merged → thank briefly, confirm issue auto-closed, record what worked (response time, template used) for future picks.

## Anti-patterns (do not do)

Arguing in review · going silent >48h on actionable feedback · force-pushing away review history mid-review · pinging multiple maintainers · opening duplicate issues to get attention · claiming urgency on volunteer time · posting near-identical first-contact comments across repos · re-commenting after a deletion or block.

## References

- Templates A–F: `references/response-templates.md`
- Tone + timing rules: `references/tone-rules.md`
