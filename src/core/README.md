# src/core/

Cross-cutting infrastructure used by all layers.

## Files

- **config.py** — `Settings` via `pydantic-settings`; reads `.env` automatically. Single `settings` singleton imported wherever config values are needed. Never use `os.environ` directly elsewhere in the codebase.
- **logging.py** — `structlog` configuration; JSON output in production (`LOG_JSON=true`), human-readable key=value in development.
- **middleware.py** — `RequestIDMiddleware`: reads or generates a `X-Request-Id` per request, binds it to the structlog context so every log line within a request carries the same id, and echoes it back on the response header.

---

[← src/](../README.md) · [← Root README](../../README.md)
