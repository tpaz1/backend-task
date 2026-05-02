# Skill Bootstrap

When the user shares the assignment spec, your job in this step is to
**generate a new skill file** that captures the domain knowledge specific to
this assignment. This skill will guide the rest of the build.

## What you produce

A single file at `.claude/skills/<assignment-slug>/SKILL.md`. The slug is
2–4 words in kebab-case derived from what the assignment actually is
(e.g. `log-event-analyzer`, `webhook-fanout-service`, `prompt-guardrail`,
`url-classifier`). Pick a slug that names the *problem*, not the company.

## What goes in the skill

### YAML frontmatter (required, must be the first content in the file)

Every SKILL.md must start with YAML frontmatter between `---` markers. This
is what allows Claude Code to discover and auto-invoke the skill in future
sessions. The skill cannot be loaded without it.

```
---
name: <assignment-slug>
description: This skill should be used whenever <specific triggers from this assignment>. It defines <list 3–5 things the skill covers, e.g. domain vocabulary, the core abstractions, the policy combination rule, the test patterns>. Claude must consult this skill before <writing any code in folder X / making decisions about Y / drafting README content about Z>.
---
```

Frontmatter rules:
- `name` must match the slug exactly. Lowercase letters, numbers, and
  hyphens only. No underscores. No spaces.
- `description` must be 1–1024 characters. Be specific about *what* the
  skill covers and *when* Claude should consult it. Skills tend to
  under-trigger, so make the description slightly pushy: list the concrete
  triggers ("whenever writing endpoints in src/api/", "before adding a new
  policy class", "when drafting the README's design decisions section").
- Use third person: "This skill should be used when..." not "Use this skill
  when...".
- The description is the *only* signal Claude has at startup for whether
  to load this skill. Vague descriptions cause skills to be ignored.

### Body sections (after frontmatter, in this order)

### 1. What this is
One paragraph. Plain English. The kind of thing you'd say to a customer.
Includes the **core verb** of the system (classifies, ingests, evaluates,
proxies, transforms, enforces, etc.) and the **inputs and outputs**.

### 2. Domain vocabulary
A glossary of 5–15 terms used in the spec or implied by the domain. Each
entry is one line. Use the exact words the spec uses, plus any obvious
adjacent terms from the field (security, networking, AI, etc.). When code
gets written, variable and function names should come from this list.

### 3. Core abstractions
3–6 types that should be first-class in the codebase. For each: name, one
sentence describing it, and the fields it likely holds. These become Pydantic
models or dataclasses. Resist adding more than 6 — extra abstractions are how
take-homes turn into over-engineered messes.

### 4. Folder layout addition
What folder(s) to add to `src/` beyond the default `api/`, `services/`,
`core/`. State the name and one sentence on what lives there. Common
candidates: `policies/`, `analyzers/`, `pipelines/`, `integrations/`,
`enrichers/`, `detectors/`, `repositories/`. Add at most two. If the default
layout works, say so and add nothing.

### 5. Key tradeoffs we'll need to articulate
3–5 tradeoffs that come from the problem itself, written as "X vs Y, and
why we'd pick one." These are the things the interviewer is most likely to
probe in the follow-up. Examples by archetype:
- A gateway: pass-through vs buffer; fail-open vs fail-closed; sync vs async.
- An analyzer: streaming vs batch; in-memory vs persistent state; exact vs
  approximate matching.
- An integration: caching strategy; retry policy; partial failure handling.
- A policy engine: rule combination order; redact vs block; precedence.

State these as questions, not answers, since the right choice depends on the
spec's exact requirements.

### 6. Test patterns specific to this domain
What kinds of tests provide the most signal. Usually one of:
- Table-driven tests over a decision boundary (best for classifiers,
  policies, evaluators)
- Snapshot tests over transformations (best for ingest/transform pipelines)
- Contract tests against a fake upstream (best for integrations)
- State-transition tests (best for stateful services, e.g. workflows)

Pick the one that fits and explain why.

### 7. What this is NOT
2–4 bullets clarifying scope. Things that look related but aren't part of
this assignment. This prevents scope creep mid-build.

### 8. Cato-flavored framing for the README
1–3 sentences using Cato's vocabulary that frame this assignment as a
simplified version of a real Cato problem space, IF AND ONLY IF the
connection is genuine. If the assignment has nothing to do with Cato's
products, leave this out — forced framing is worse than no framing.

## How to write it

- Be concrete. "A request" is bad; "an HTTP request to be inspected before
  forwarding" is good.
- Use the spec's exact vocabulary when possible. If the spec says "event,"
  the skill says "event," not "message" or "record."
- Don't invent things the spec doesn't mention. If the spec says nothing
  about persistence, the skill doesn't recommend a database.
- Keep it under 400 lines. Skills are working documents, not textbooks.

## After writing the skill

Show the full skill content to the user in chat. Ask for any corrections
before moving on. Then proceed to Step 3 of the workflow in CLAUDE.md
(propose 2 design options).

## Example slug + frontmatter + section 1 for calibration

If the spec said: "Build a service that ingests HTTP request logs from a
proxy, identifies which GenAI applications are being used, and exposes an
API to query usage by user and time range":

- Slug: `shadow-ai-discovery`
- Frontmatter:
  ```
  ---
  name: shadow-ai-discovery
  description: This skill should be used whenever writing code for the GenAI usage discovery service in this project — log ingestion, app classification, the queryable inventory, or the user/time API. It defines the domain vocabulary (events, sources, sanctioned/unsanctioned apps, fingerprints), the core abstractions (LogEvent, AppFingerprint, UsageRecord), the classification approach, the in-memory vs persistent state tradeoff, and the table-driven test pattern for the classifier. Claude must consult this skill before adding any classifier rule, ingestion endpoint, or query endpoint.
  ---
  ```
- Section 1: "A service that ingests HTTP request logs from network proxies
  and identifies which GenAI applications are being used by which users.
  Inputs: structured log events (one per HTTP request). Outputs: a queryable
  inventory of GenAI usage broken down by user, application, and time. The
  core verb is **classify** — match each log line to a known AI application
  fingerprint, or mark it unknown."
