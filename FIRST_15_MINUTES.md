# First 15 Minutes Playbook

When the assignment lands, resist the urge to start coding. The first 15
minutes are worth more than any other 15. Spend them like this.

## Minute 0–5: Read the spec twice

Both reads with no laptop touched. On the second read, mark up:

- **Hard requirements** — things explicitly demanded
- **Soft requirements** — things implied or "nice to have"
- **Ambiguities** — things you'd ask the interviewer if you could
- **Out of scope** — things the spec rules out

## Minute 5–10: Bootstrap a domain skill

This is the most important step in the whole process.

Open Claude Code in the project. Paste this prompt with the spec attached:

> Read CLAUDE.md, then read .claude/skill-bootstrap.md. Then read the
> assignment spec below. Follow the bootstrap instructions to generate a new
> skill at .claude/skills/<assignment-slug>/SKILL.md. Show me the full skill
> content in chat. Do not write any code or modify the source.
>
> [paste spec]

Claude Code will produce a tailored skill capturing the domain vocabulary,
core abstractions, key tradeoffs, and test patterns specific to *your*
assignment.

Read the generated skill carefully. This is the single most important
artifact you'll create — it determines everything that follows. Push back on
anything that's wrong:

- Missing or wrong vocabulary? Tell Claude Code which terms to add or fix.
- Wrong core abstractions? Say what they should be.
- Missing tradeoffs? Add them.

Iterate until the skill is right. Don't move on until you'd be comfortable
showing the skill file to the interviewer.

## Minute 10–13: Pick a design

With the skill in place, ask Claude Code:

> Now propose 2 design options for this assignment. For each: which folders
> we add to src/, what the core abstractions are (Pydantic models),
> what's persisted vs in-memory, what the request flow looks like. Don't
> write code yet.

Pick one. Disagree if needed.

## Minute 13–15: Lock the walking skeleton plan

Tell Claude Code:

> Going with option N. Write me a 30-minute plan for the walking skeleton:
> the smallest end-to-end thing that returns a real response. List files in
> the order they'll be created. No code yet.

Once the plan looks right, say "go" and let it build.

## Minutes 15–160: Build

Follow the plan. After every meaningful chunk:

- Run `make test`
- Run `make lint`
- Look at the diff before accepting

Do not let Claude Code build more than 15 minutes of work without you reading
the output.

## Last 20 minutes — non-negotiable

At the 2:40 mark, stop building features. Use the remaining 20 minutes for:

1. README — fill in the design decisions, "more time", and "didn't build"
   sections with real, specific items from your build
2. Run the full test suite one final time
3. `git log --oneline` — clean up commit messages if any are nonsense
4. Read your own code in the order a reviewer would: README → structure → one
   router → one service → one test
5. If anything looks AI-generated (over-commented, padded, weird abstractions),
   delete it

## Things that go wrong

- **Spec is bigger than 3 hours allows.** Cut features explicitly. Mention
  the cut in "What I deliberately did not build" with reasoning. Reviewers
  respect judgment more than completeness.
- **The bootstrap skill turns out wrong mid-build.** Stop and update it.
  It's a working document, not stone tablets. A 5-minute skill update saves
  you from 30 minutes of misdirected code.
- **You disagree with Claude Code.** You're right by default — you're the one
  presenting it. Override.
- **You're stuck on a hard sub-problem at the 2-hour mark.** Stop. Implement
  the simplest version that works (even if hardcoded), and put "robust X" in
  "more time". Working > elegant.
- **A test fails in the last 10 minutes.** Either fix it immediately (under 5
  min) or delete the failing test, mark it skip, and note in the README that
  it's a known issue. Never submit with a failing test you can't explain.

## Why the bootstrap pattern matters

The skill you generate from the spec is more valuable than any skill I could
have pre-written, because it uses the spec's exact vocabulary and abstractions.
When the interviewer asks "why is your code organized this way?", the answer
is: *"I extracted the domain model from the spec — these are the nouns the
spec uses, and these are the verbs. The folder layout follows that vocabulary.
The tests cover the decision boundary the spec describes."*

That's a much better answer than "I followed a pattern I had lying around."
