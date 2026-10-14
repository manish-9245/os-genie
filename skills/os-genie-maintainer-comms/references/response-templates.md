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

## H. First-contact claim (approval already quoted, block-risk passed)

Use only when triage scored >= 60 AND `claim-guide.md` section 1 passes on
all four checks. Read the code first: no trace, no comment. 5 to 9 lines
for bugs, 4 to 7 for docs. Never reuse a sentence from another claim within
30 days.

> Per [maintainer comment link or label saying yes]: traced it to
> [file:line, function], where [suspect expression] lets [bad outcome]
> through. Reproduced on [version] with [input]: [observed result].
> I think the root cause is [cause], though [one honest uncertainty].
> Proposal: [change], keeping [boundary: what stays untouched]. Considered
> [alternative] but rejected it because [reason]. Does [binary question]
> match what you'd merge?

Why: approval first, trace from the source, root cause with evidence,
rejected alternative proves thought, boundary stated, question closes.
"Please assign me" appears nowhere; the question does the asking.

## I. Scope question instead of a claim (no approval yet)

Use when approval is missing, a maintainer question is still open, or the
block-risk check fails softly (-10 tier). Do not claim, do not propose a
PR, do not ask for assignment. Still show the trace: an undecided issue
earns attention through investigation, not keenness.

> Reading the thread, the open point seems to be [maintainer name, date:
> quoted question]. I looked at [file:line, function]: [what the code
> currently does, one line]. Repro on [version]: [observed result]. If that
> resolves toward [X], the change looks like [file and section, one line],
> keeping [boundary]. Would you want [X], or is this already covered?

Why: answers the thread as it stands, proves time in the codebase, requests
a decision rather than permission. On a yes, follow up with Template H shape
plus diff. Full rules: triage `references/claim-guide.md`.
