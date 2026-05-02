# src/

Source tree for the Aim Prompt Guardrail service.

The one architectural rule that must not break: `services/` and `classifiers/` never import from `api/` or from FastAPI. This is what makes the business logic unit-testable without an HTTP server — the LLM classifier and all orchestration logic can be exercised with plain `pytest` and no running application.

## Subdirectories

- [api/](api/README.md) — Thin FastAPI routers. HTTP in, HTTP out. No business logic.
- [services/](services/README.md) — Business logic. Framework-agnostic. No FastAPI imports.
- [classifiers/](classifiers/README.md) — LLM I/O isolation. The only code that talks to OpenAI.
- [core/](core/README.md) — Cross-cutting infrastructure: config, logging, middleware.
- [models/](models/README.md) — Pydantic domain types shared across all layers.

---

[← Root README](../README.md)
