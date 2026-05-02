---
name: tradeoff-writing
description: This skill should be used whenever writing or editing the README's "Design decisions", "What I'd do with more time", or "What I deliberately did not build" sections, and when the user asks how to articulate or defend a technical choice. It defines the four-part bullet structure ("I chose X over Y because Z. The tradeoff is W."), what makes a tradeoff worth surfacing, the right altitude for decisions in a 3-hour assignment, how to translate engineering choices into customer-facing language for the interview follow-up, and how to prepare verbal versions of each tradeoff. Claude must consult this skill before drafting any tradeoff content.
---

# Tradeoff Writing

The "Design decisions" section of the README is the single most-read part of
a take-home. It's also where you signal seniority. This skill is about how
to write it.

## The shape of a good tradeoff bullet

> I chose **X** over **Y** because **Z**. The tradeoff is **W**.

Four parts. Concrete. Names a real alternative. Names a real cost.

**Bad**: "I used FastAPI because it's modern and fast."
- No alternative. No cost. Says nothing.

**Good**: "I chose FastAPI over Flask because the assignment requires
auto-generated OpenAPI documentation for customer-facing usage. The tradeoff
is a heavier dependency footprint and slightly more boilerplate for simple
endpoints."

## What makes a tradeoff worth writing about

A tradeoff is worth surfacing when:

1. **The alternative was real.** You actually considered it. Not a strawman.
2. **The cost is real.** Not "the only downside is it's better."
3. **The reader might disagree.** If the choice is obvious to everyone,
   don't waste a bullet on it. Use bullets for the choices where a competent
   reviewer might say "why did you do that?"

## Pick decisions at the right altitude

For a 3-hour assignment, the right altitude for tradeoff bullets is usually:

- **Architecture-level**: layering, where logic lives, what's pure vs
  side-effectful
- **Persistence**: in-memory vs SQLite vs nothing; sync vs async
- **Failure handling**: fail-open vs fail-closed; retry policy; timeout
  behavior
- **Data modeling**: one schema vs separate request/response/domain models;
  list vs map for some collection
- **Domain-specific**: rule precedence, matching strategy, what to log

Avoid:
- Choosing the language (you didn't, the spec did)
- Choosing pytest (it's the default, no one will challenge it)
- Choosing Docker (everyone uses Docker)

## Connect tradeoffs to the role

For a customer-facing role, frame tradeoffs in terms a customer or PM would
care about. "Lower latency" is engineering. "Faster response visible to end
users" is product. Translating tech decisions into customer-facing language
is the core skill being tested.

## "What I'd do with more time" — same shape

These bullets are also tradeoffs, just with the time axis. Each bullet
should:

1. Name a real gap in the implementation
2. Explain why it matters (in customer terms when possible)
3. Be specific enough that a reviewer believes you'd actually do it

**Bad**: "Add more tests."
**Good**: "Add property-based tests using Hypothesis on the rule combiner —
the current table-driven tests cover obvious cases, but rule precedence has
combinatorial behavior that's worth fuzzing before this ships."

## "What I deliberately did not build" — judgment signals

These bullets are the most underrated part of the README. They show you
identified scope creep and said no.

**Bad**: "I didn't build authentication."
**Good**: "I did not build authentication or multi-tenancy. The spec didn't
require them, and adding fake versions would obscure the actual policy
logic. In production, this service would sit behind an authenticated gateway
that already does tenant isolation."

The pattern: state what's missing → why you cut it → where the real version
would live in a deployed system.

## Verbal version for the interview

For the follow-up call, prepare a 30-second verbal version of each tradeoff
bullet. Practice saying them aloud. Interviewers ask "why did you do X?" —
you should be able to answer in three sentences without filler.
