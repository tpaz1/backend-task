# tests/

12 tests across two tiers. Run with `make test`.

## Strategy

**unit/** — Classifier decision boundary. The OpenAI client is mocked; no I/O, no network. Tests cover the four topic categories, a multi-topic prompt, an off-topic prompt, a malformed LLM response (expect `ValueError`), and the `classify_fast` at-most-one guarantee. Table-driven with `pytest.mark.parametrize`.

**integration/** — End-to-end through the HTTP layer. The classifier functions are overridden via `app.dependency_overrides` so no LLM calls are made, but every other layer (routing, service logic, audit store, exception handlers) runs for real. One happy-path test per endpoint.

## What's not here

Live-system checks (container running, real LLM calls, latency benchmarking) live in `scripts/smoke_test.sh` and are not part of `make test`. See [scripts/README.md](../scripts/README.md).

---

[← Root README](../README.md)
