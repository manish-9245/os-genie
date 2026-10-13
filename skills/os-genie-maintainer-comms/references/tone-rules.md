# Tone + timing rules: os-genie-maintainer-comms

## Tone

- Assume good intent; review is collaborative, not adversarial (Google Eng Practices; opensource.guide).
- Short sentences, plain words. Link evidence instead of narrating it.
- State constraints honestly: "I couldn't reproduce on [env]; here's what I tried" beats guessing.
- Never: flattery openers, urgency demands ("ASAP", "blocker" for non-security), @-mentioning uninvolved maintainers, or AI self-reference.

## Timing

| Situation | Rule |
|---|---|
| Review feedback actionable | Reply + fix within 48h, or post a same-day ETA |
| Asked a question, no answer | Wait 7 days before bumping |
| Bumped twice, still silent | Stop; log repo as unresponsive for repo-finder scoring |
| Asked to make big changes | Acknowledge <24h, propose split (Template E), implement agreed scope |
| After pushing fixes | Re-request review explicitly; don't assume they noticed |

## Per-comment hygiene

- Address ALL comments, including nits. Mark resolved only after pushing the fix.
- Step away if frustrated; never reply heated. Re-read before sending: would you merge from a contributor who wrote this?
- Keep follow-ups on the same PR branch; keep new scope in a new PR.
- Record outcomes (template used, reply latency, merge result), it trains your future repo picks.
