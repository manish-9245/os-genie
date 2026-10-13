# Response templates: os-genie-maintainer-comms

Copy, fill brackets, keep under 8 lines before any log/code block.

## A. Ask a scope doubt (before coding)

> Working on #123 (`one-line scope`). I checked [docs/PR #X] and tried [what you tried].
> Two options: (1) [minimal option]: [tradeoff]; (2) [broader option]: [tradeoff].
> I recommend (1) because [reason]. Does that match what you'd accept?

Why: proposes in-issue first and waits for approval, avoids unsolicited-feature rejection.

## B. Agree with review

> Good catch, fixed in [`abc1234`]. [One line on what changed.]

One reply per thread, or a single summary listing each point + commit.

## C. Need clarification

> I want to make sure I understand: are you suggesting [X] because of [Y]? My read was [Z]. Happy to switch to [X] once confirmed.

Binary questions get answers; open "what do you mean?" gets silence.

## D. Respectful disagreement

> I went with [current approach] because: (1) [reason + data/link]; (2) [reason].
> Open to changing to [alternative] if you think it better serves [project goal]. Just say the word.

Defer explicitly. Never relitigate after a maintainer decides, implement their call.

## E. Big ask → propose follow-up split

> Great suggestion. To keep this PR reviewable (<200 lines), would it make sense to land [current scope] here and address [big ask] in a follow-up PR? Happy to open it right after.

Data anchor: large PRs slow review and miss issues (LinearB 2025).

## F. Polite bump (≥7 days, CI green)

> Friendly bump, this is green and ready for review when you have a moment. Summary: [1 line]. Happy to adjust anything. (Refs #123)

One bump per 7 days, max two, then stop and log responsiveness.

## G. Graceful close (wontfix / stale)

> Understood, thanks for explaining. Closing this out: [one-line learning]. Happy to help elsewhere.

No arguing, no parting shots. Reputation compounds across repos.
