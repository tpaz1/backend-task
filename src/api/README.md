# src/api/

Thin FastAPI routers. This layer translates HTTP requests into service calls and HTTP responses — nothing more. No business logic lives here.

## Files

- **detection.py** — `POST /detect` and `POST /protect` endpoints; delegates immediately to `services/detection.py`.
- **audit.py** — `GET /logs` endpoint; returns the full audit trail from `AuditStore`.
- **health.py** — `GET /health` liveness probe; returns `{"status": "ok"}` with no dependencies.

Exception handlers for `ValueError` (classifier parse failure → 502) and `openai.APIError` (LLM error → 502) are registered in `main.py`, not here, so they apply across all routers.

---

[← src/](../README.md) · [← Root README](../../README.md)
