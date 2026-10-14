# Tone + timing rules: os-genie-maintainer-comms

## Tone

- Assume good intent; review is collaborative, not adversarial (Google Eng Practices; opensource.guide).
- Short sentences, plain words. Link evidence instead of narrating it.
- State constraints honestly: "I couldn't reproduce on [env]; here's what I tried" beats guessing.
- Never: flattery openers, urgency demands ("ASAP", "blocker" for non-security), @-mentioning uninvolved maintainers, or AI self-reference.

## Anti-AI-detection (first-contact comments get scanned as bot output)

Detectors key on repetition across issues plus generic phrasing, not on any
single word. Rules:

- Never reuse a sentence verbatim across issues within 30 days. Vary the
  opener, the plan phrasing, and the closer every time.
- Banned openers and closers: "Hi, I'd like to fix this", "I would like to
  work on this", "Please assign me", "I am excited to contribute", "Hope
  you're doing well", "Small PR coming. Thanks!". If your draft matches any
  of these skeletons with only nouns swapped, rewrite it.
- Every first contact names a concrete artifact: file path, function,
  docs section, or quoted line from the thread. No artifact means no post.
- One clause of real credibility ("hit this running X on Y"), zero resume,
  zero flattery, zero emoji, zero section headers in a short comment.
- Plain punctuation only. No em dash character anywhere in the repo or in
  posted comments (house rule). Use commas or colons.
- Read-back test: cover the issue title and ask whether this comment could
  only belong to this thread. If it fits any of your last five claims, it
  is a template, rewrite it.

## Word-level tells (what readers and detectors actually score)

Sources: Pangram signs-of-AI study (millions of docs, em dashes 10x,
list-instead-of-prose 9x, Rule of Three 4x, not-just-X-but-Y 3x),
Wikipedia Signs of AI writing, humzakt/ai-writing-markers dataset,
Humanetext and Syxo 2026 humanizing guides. No single marker means
anything; density across categories is the signal. The goal is not
generic-human but a specific human with specific knowledge.

1. Banned vocabulary (measurably overrepresented in model output): delve,
   tapestry, testament, realm, pivotal, robust, seamless, leverage,
   utilize, streamline, unlock, navigate, elevate, transformative,
   synergy, harness, meticulous, plethora, myriad, showcase,
   ever-evolving. Use the plain word: use, help, show, start.
2. Banned shells and transitions: "It is important/worth noting that",
   "Importantly", "Interestingly", "Moreover", "Furthermore",
   "Additionally" to open, "In conclusion", "In today's fast-paced
   world", "When it comes to". Delete the shell, keep the point. If the
   point needs no shell, it was filler.
3. Banned shapes: Rule of Three adjective strings ("fast, reliable, and
   scalable"), "not just X but Y" / "not only X but also Y", "serves as
   a" for "is", "features" for "has", vague attribution ("studies show",
   "reviewers note"). Break parallels, state the claim directly.
4. Formatting: no bold, headers, emoji, or bulleted lists in a 5 to 9
   line comment. Humans typing in a comment box write prose; lists with
   bold lead-ins are assistant register. Code spans and file paths are
   fine, they are content, not decoration.
5. Rhythm: mix short sentences (3 to 8 words) with long ones (25 plus).
   Detectors call this burstiness, readers call it sounding like
   thinking. An occasional And, But, or So starter is fine, people talk
   that way. Read the draft aloud; wherever you stumble, rewrite.
6. Position over hedge: allow may, could, or potentially only where
   uncertainty is real (your one honest uncertainty). As default register
   they read evasive. Say what you think.
7. Specifics over categories: one number, name, date, or version per
   comment minimum. Generic claims are the safe average of everything;
   particular facts are what only someone who did the work can state.
8. Never paste chatbot artifacts: contentReference, oaicite,
   turn0search0 markers, curly quotes lifted from a chat window,
   zero-width characters. Draft in plain text.
9. Synonym-swapping flagged words changes nothing; the same distribution
   produced the synonyms. Fix rhythm, add specifics, cut shells, take a
   position, break parallels, in that order.

## Reason like a human (think out loud, briefly)

- Walk the trace in order: what you opened, what you saw, what you
  concluded. Two sentences of path beat a paragraph of verdict.
- State one uncertainty honestly ("not sure yet whether X or Y, leaning X
  because..."). Certainty about everything reads generated; working
  engineers hedge once, then commit.
- Name one dead end or rejected alternative with its reason. Proof of
  exploration is what separates "spent time in the codebase" from "read
  the issue title".
- Keep it short anyway: trace plus cause plus proposal plus question,
  then stop. Thinking out loud is not thinking at length.

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
