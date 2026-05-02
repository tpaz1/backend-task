# CLAUDE.md

You are helping me complete a 3-hour take-home assignment for an **AI Security
Solutions Architect** role at Cato Networks. After submission, I will present
and defend every line of code in a follow-up interview. Optimize for **code I
can explain**, not code that looks impressive.

## Hard constraints

1. **Time budget is 3 hours.** Do not propose work that doesn't fit. If you
   think something will take more than 20 minutes, flag it and propose a
   simpler version first.
2. **Every change must be explainable in one sentence.** If you cannot justify
   a line of code in plain English, do not write it.
3. **Explain before you code.** For any non-trivial change, write a short plan
   in chat (3–8 lines: what, why, tradeoffs) and wait for me to ack before
   editing files. Trivial = a typo, a one-line fix, a rename.
4. **No new dependencies without asking.** The stack is fixed (see below).
5. **No invented requirements.** If the spec doesn't ask for it, don't build
   it. When in doubt, ask me.
6. **No assumptions about what the assignment is.** This skeleton is generic.
   Until I share the spec, do not assume what kind of service we're building.

## Stack (fixed — do not deviate without asking)

- Python 3.11+
- FastAPI + Pydantic v2
- httpx for outbound HTTP (only if the spec requires outbound calls)
- structlog for logging
- pytest + pytest-asyncio + httpx.AsyncClient for tests
- uv for dependency management
- ruff for lint/format, mypy for typing
- Docker + docker-compose for run
- SQLite via SQLAlchemy 2.0 async — only if persistence is required by the spec

If the spec demands a different tool (e.g. Redis, Kafka, a specific ML lib),
ask before adding. Don't add "just in case".

## Architecture rules

- Default layers: `api/` (HTTP), `services/` (business logic), `core/`
  (config, logging, middleware). Add domain-specific folders **only after we
  agree** what they should be (e.g. `policies/`, `analyzers/`, `pipelines/`,
  `integrations/`).
- `api/` modules import from `services/`. `services/` never import from `api/`
  or from FastAPI. This is the one rule that must not be broken.
- Config goes in `core/config.py` via Pydantic `BaseSettings`. Read env vars,
  not `os.environ` scattered around the codebase.
- Logging is structured (structlog), JSON in prod, human-readable in dev.
  Every request gets a `request_id`. The skeleton already wires this up.

## Code style — mandatory

- Type hints on every function signature. No `Any` unless justified in a
  comment.
- Functions short, named after what they do. `evaluate(...)` not
  `evaluator(...)`.
- Comments explain **why**, never **what**. If the code needs a comment to
  explain what it does, rewrite the code. Exception: a one-line docstring on
  every public service method stating its contract.
- No defensive programming for impossible cases. Trust your types.
- No try/except that just re-raises or logs and re-raises. Catch only what you
  can handle meaningfully.
- Prefer pure functions in `services/`. I/O lives at the edges.
- Use `X | None`, not `Optional[X]`.

## AI-generated-code smells to actively avoid

These are dead giveaways that code was written by an LLM. Reviewers spot them.
Do not:

- Add a comment above every line ("# Initialize the FastAPI app").
- Use `print()` statements left over from debugging.
- Wrap simple things in `try/except Exception: pass` "for safety".
- Generate verbose docstrings with `Args:`, `Returns:`, `Raises:` sections for
  internal helpers. Public service methods get one-line docstrings. Internal
  helpers get none if the name is clear.
- Add abstractions ("ServiceFactory", "AbstractHandlerBase") that have
  exactly one implementation.
- Generate placeholder TODO comments. Either implement it or leave it out.
- Pad responses with summaries of what you just did.

## Test philosophy

- Tests document behavior. Test names read as English sentences.
- One assertion per test where possible. Multi-assert tests need a comment
  explaining why they belong together.
- Cover the **decision boundary** of whatever the assignment's core logic is.
  Table-driven tests are usually the right shape.
- Don't chase coverage. 100% coverage on a 3-hour assignment looks like
  padding.
- Integration test: one happy-path end-to-end test through the API per
  endpoint. That's enough.

## Workflow — read carefully, this is the actual process

When I share the assignment spec, follow this order strictly:

### Step 1 — Summarize, don't code (5 min)
Read the spec twice. Then summarize it back to me in 5–10 bullets including
any ambiguities. Do not start coding.

### Step 2 — Bootstrap a domain skill (5 min)
Read `.claude/skill-bootstrap.md`. Follow its instructions to generate a new
skill file at `.claude/skills/<assignment-slug>/SKILL.md` capturing the
domain vocabulary, core abstractions, key tradeoffs, and patterns specific to
this assignment. Show me the skill before continuing. This is the most
important step — once this skill exists, you have domain awareness for the
rest of the build.

### Step 3 — Propose 2 design options (5 min)
With the domain skill in place, propose 2 design options with tradeoffs.
Specifically: what folders to add to `src/`, what the core abstractions are,
what gets persisted vs in-memory.

### Step 4 — Walking skeleton plan (5 min)
Once we pick a design, write a 30-minute plan: the smallest end-to-end thing
that returns a real response. List files to create or edit. Do not write
code yet.

### Step 5 — Build (rest of time minus 20 min)
Build the walking skeleton, then iterate. After each meaningful chunk: run
tests and lint. Stop and show me the diff before moving on if anything is
unexpected.

### Step 6 — Final 20 minutes — non-negotiable
Stop adding features. README, polish, commit history cleanup, final test run.
Reserve this. Do not let it get squeezed.

## README requirements

The README is graded as heavily as the code. It must contain:

- **What it is** — one paragraph, plain English, customer-readable.
- **How to run it** — `docker compose up` and `make test`. Nothing else.
- **API** — link to `/docs` and one curl example per endpoint.
- **Design decisions** — 3–5 bullets, each of the form "I chose X over Y
  because Z. The tradeoff is W."
- **What I'd do with more time** — 3–5 bullets. Honest. This is where I
  demonstrate that I know what's missing.
- **What I deliberately did not build** — 2–3 bullets. This shows judgment.

See `.claude/skills/tradeoff-writing/SKILL.md` for how to articulate these.

## Domain context (background, not a prediction)

The role is at Cato Networks, a SASE company with a CASB product and an AI
Security product line. Their products handle policy enforcement, audit
logging, traffic inspection, and AI/GenAI governance. **The assignment could
be anything in the backend space.** Do not assume it's about AI gateways or
policy engines until the spec confirms it. Use Cato vocabulary in code and
docs only when it actually fits the spec.

## When I push back

If I disagree with something you wrote, do not capitulate immediately. Defend
your reasoning once if you believe you were right. If I still disagree, do it
my way — I'm the one presenting it.
