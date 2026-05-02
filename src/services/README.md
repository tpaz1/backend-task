# src/services/

Business logic layer. No FastAPI imports — these modules are plain async Python and can be called directly from tests without an HTTP server.

## Files

- **detection.py** — `detect()` and `protect()` orchestration functions. Each resolves the enabled topic list, calls the appropriate classifier function, writes an audit entry, and returns a `DetectionResult`. Short-circuits without an LLM call when all settings are disabled.
- **audit.py** — `AuditStore` class (append-only in-memory list) and `get_audit_store()`, a module-level singleton returned via FastAPI `Depends`. All requests share the same store instance within a process lifetime.

---

[← src/](../README.md) · [← Root README](../../README.md)
