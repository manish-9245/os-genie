# Claim guide: os-genie-issue-triage

How to ask for an issue without reading as a bot and without getting blocked.
This guide is mandatory before drafting any claim comment. It exists because
of a real 2026-10-14 incident: 13 near-identical claim comments in 24h got
`manish-9245` blocked by the pallets org on `pallets/flask#6146`, comment
deleted, fork PR path closed ("Only collaborators can create PRs"). Two prior
contributors were blocked on the same issue for the same behavior.

## 1. Block-risk check (run first, before any draft)

Do all four. Any FAIL means do not claim; ask a scope question instead
(maintainer-comms Template I) or drop the issue.

1. **Approval present?** Maintainer comment saying yes, welcome, confirmed,
   or a triaged/confirmed/accepted label, or a milestone. No approval means
   no claim. Pallets #6146 failed here: maintainer `davidism` was still
   questioning the upstream example, author `hoodmane` was waiting on a
   yes/no. A claim there answers a question nobody asked.
2. **Issue timeline clean?** Load the full timeline
   (`gh issue view <n> --repo <o/r> --comments`, plus the web timeline for
   org events). If you see "blocked <user>" or "deleted a comment from
   <user>" events, especially 2 or more, the maintainers are actively
   removing drive-by claims. Walk away regardless of score.
3. **Contribution path open?** Read CONTRIBUTING plus the repo PR list and
   the issue page notice. Red flags: "Only collaborators can create PRs",
   "please do not comment asking to be assigned", assignment via an external
   tracker, or every recent first-timer PR closed unmerged. If the path is
   closed, a claim cannot convert; log it and pick another issue.
4. **Collision fresh?** Re-check assignees, linked PRs, and "working on it"
   comments under 30 days old right before drafting. State changes fast;
   a morning check does not cover an afternoon post.

## 2. Velocity limits (hard caps)

Bot detectors key on volume and rhythm, not just wording.

- Max 5 first-contact comments per 24h across all of GitHub, max 2 per org
  per 24h, max 1 per issue ever (edit that comment if the plan changes).
- Space first contacts at least 60 minutes apart. Never batch post.
- No claims on weekends for repos with no weekend maintainer activity;
  the comment sits, others pile on, and Monday starts with a cleanup block.
- New accounts (under 6 months) or accounts with under 5 merged PRs halve
  the caps above. Low history plus high volume is the classic bot signature.
- One thoughtful merged PR beats ten claims. If you already have 3 or more
  unanswered claims, stop claiming and implement what you have.

## 3. Show your work (read the code before you write the comment)

No comment goes out unless you have opened the repo and traced the issue
yourself. The comment must read like someone who spent real time in the
codebase, because you did. Minimum homework before drafting:

1. **Explore the codebase:** find the exact file and function where the bug
   lives or the docs section to change. Name `path/to/file.py:line` and the
   enclosing function. If you cannot name a line, keep reading, do not post.
2. **Trace the bug out loud:** one or two sentences walking the call chain
   (caller to failing line), quoting the suspect expression. State what you
   believe the root cause is and what evidence supports it (repro output,
   log line, test run with version). One honest uncertainty is fine and
   reads human ("not sure yet whether X or Y, leaning X because...").
3. **Fix proposal with a boundary:** what you will change, one alternative
   you considered and rejected with a reason, and what you will explicitly
   not touch. This is the proof of thought; a plan with no rejected
   alternative reads generated.
4. **A real question or decision:** binary and specific (approach A vs B,
   test to add, page to edit). Close with the question, not with "please
   assign me" or "thanks in advance".
5. **Credibility, one clause only:** "hit this running X on Y" or "use this
   via Z". Never a resume, never flattery, never urgency.

Structure: trace (1 to 2 lines) + root cause with evidence (1 line) +
proposal with rejected alternative and boundary (1 to 2 lines) + question
(1 line). 5 to 9 lines total for bugs, 4 to 7 for docs. If you cannot fill
the trace, you have not earned the comment yet.

## 4. Anti-patterns (each one caused a real block or ignore)

- Identical openers across issues ("Hi, I'd like to fix this. Plan: ...").
  Vary every comment; never reuse a sentence verbatim within 30 days.
- Template skeleton with only nouns swapped (same line count, same
  "Small PR coming. Thanks!" closer). Maintainers diff claims mentally.
- Claiming with zero approval to "reserve" the issue. Reservations are spam.
- "Please assign me", "I am excited to contribute", "Hope you're doing
  well", em dashes, emoji, or bold/italic section headers in a 5-line
  comment. None of these appear in human first contacts on these threads.
- Posting the fix as a PR within minutes of the claim with no discussion
  on a scope-undecided issue. It reads as farming, not helping.
- Re-commenting after a deletion or block, or opening a PR to route around
  it. That converts a per-issue block into an org-wide one.

## 5. Good vs blocked (with a real trace)

Blocked (pallets #6146 pattern, comment deleted, account blocked):

> Hi, I'd like to fix this docs bug. Plan: add the link, single docs PR.
> Small PR coming. Thanks!

Why it failed: no approval quoted (maintainer had not said yes), no file
named, no mention of the open maintainer question about the upstream
example, identical skeleton to 12 sibling comments posted the same day.

Acceptable shape for that docs issue (scope question, thread-aware):

> Reading this thread, the open question from davidism (Aug 31) is whether
> the upstream Cloudflare example now exists, hoodmane confirmed Sep 1 it
> was merged. If that resolves it, the docs edit looks like one line under
> "Hosting Platforms" in docs/deploying/index.rst. Would you still want
> that link, or is this already covered? Happy to add it if yes.

Why it survives: quotes the actual thread state, names the file and
section, proposes nothing until the maintainer answers, asks a binary
question. On approval, a short follow-up with the diff is natural.

Acceptable shape for a code bug (trace first, proposal second):

> Traced this a bit: `sanitize_value_for_csv` in `gradio/utils.py` guards
> prefixes `=`, `+`, `-`, `@` but never checks `\r`, so a `\r` payload
> sails through and a spreadsheet still executes the cell. I reproduced it
> locally on 5.x with a `=cmd|...` value prefixed by `\r` (OWASP lists
> `\r` alongside `=` for this reason). Fix looks like adding `\r` (and
> `\t` while there, both are formula-prefix chars) to `unsafe_prefixes`
> plus a unit test on the `\r`-prefixed case. Considered stripping instead
> of prefixing but that would change stored values, so prefix guard only.
> Does prefix-only match what you'd merge, or do you want the strip variant?

Why it reads human: exact function named, call outcome described, repro
with version, root cause stated, one rejected alternative with a reason,
boundary implicit (no storage change), ends on a binary question. No two
bugs share a skeleton because no two traces read alike.

## 6. Pre-post checklist

- [ ] Approval quoted with comment link or label name
- [ ] Timeline checked for prior blocks or deletions
- [ ] Contribution path verified open (CONTRIBUTING + PR list)
- [ ] Code actually opened: file:line named, trace written from the source
- [ ] Root cause stated with evidence (repro, log, version), one honest uncertainty allowed
- [ ] Proposal names a rejected alternative with a reason, plus an explicit boundary
- [ ] No sentence reused from another claim in the last 30 days
- [ ] Wording passes the tone-rules word-level scan (no banned vocab,
  shells, shapes, or comment-box formatting tells)
- [ ] Velocity caps respected (5/day global, 2/org, 60 min spacing)
- [ ] Ends with a question, 5 to 9 lines for bugs, 4 to 7 for docs
