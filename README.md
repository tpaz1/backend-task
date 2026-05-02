# [Project name — fill in once spec is read]

> One-paragraph customer-readable summary. What does this service do, and why
> would someone use it? Aim for the first sentence to be understandable by a
> non-engineer.

## Run it

```bash
docker compose up --build
# API on http://localhost:8000
# Interactive docs: http://localhost:8000/docs
```

Run tests:

```bash
make install
make test
```

## API

Auto-generated OpenAPI spec at `/docs`. Quick examples:

```bash
curl http://localhost:8000/health
# → {"status":"ok"}

# [Add one curl example per endpoint, with a real-looking request body]
```

## Design decisions

Each bullet is "I chose X over Y because Z. The tradeoff is W."
See `.claude/skills/tradeoff-writing/SKILL.md` for guidance on writing these.

- **[Decision 1]** — fill in based on what you actually built
- **[Decision 2]**
- **[Decision 3]**

## What I'd do with more time

3–5 honest, specific items. This is where I demonstrate I know what's missing.

- [Item 1 — be specific, name the customer-facing benefit]
- [Item 2]
- [Item 3]

## What I deliberately did not build

2–3 items that show judgment.

- [Cut 1 — what's missing, why I cut it, where the real version would live]
- [Cut 2]

## Repository layout

```
src/
  api/      HTTP routers — thin, no business logic
  services/ Business logic — pure where possible, framework-agnostic
  core/     Config, logging, middleware
  [domain folder added based on the assignment, e.g. policies/, analyzers/]
tests/
  unit/        Domain tests, no I/O
  integration/ End-to-end through the API
```

The one architectural rule: `services/` and `[domain folder]` never import
from `api/` or from FastAPI. This is what makes the business logic
unit-testable.
