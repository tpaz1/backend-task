# src/classifiers/

LLM I/O isolation. This is the only file in the codebase that instantiates the OpenAI client or makes API calls. Swapping the LLM (different model, different proxy, function-calling vs JSON mode) is contained entirely here.

## Public functions

- **`classify_all(prompt, enabled_topics)`** — Sends a single request asking the model to identify all matching topics. Returns a list of zero or more topic strings.
- **`classify_fast(prompt, enabled_topics)`** — Sends a compact single-instruction prompt asking for the first match. Enforces the at-most-one guarantee with a `[:1]` slice regardless of what the model returns.

## Invariants

Every topic name returned by either function is lowercased and filtered against the known-valid set (`health`, `finance`, `legal`, `hr`) before it leaves this module. `"Health"` and `"HEALTH"` never reach the service layer or audit log.

On JSON parse failure the module raises `ValueError`. On OpenAI API error it raises `openai.APIError`. Both are caught by exception handlers in `main.py` and mapped to HTTP 502 (fail-closed).

---

[← src/](../README.md) · [← Root README](../../README.md)
