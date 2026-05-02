# Aim Prompt Guardrail

A topic-detection service that acts as an inline security layer for GenAI pipelines. Before a user prompt reaches a downstream model, this service inspects it and identifies which sensitive topic categories it touches — healthcare, finance, legal, or HR. Callers configure which topics to enforce per request and choose between two detection modes: `/detect` waits for a complete classification across all enabled topics, while `/protect` is the fail-fast variant optimised for inline enforcement, returning as soon as it identifies the first match. Every call is recorded in an append-only audit log accessible via `/logs`.

This is a simplified version of the inline prompt inspection pattern used in modern AI security gateways. It mirrors the audit-mode vs enforce-mode split common to that product category — including in Aim Security's AI Firewall, now part of Cato's AI Security product line. The detect/protect split maps directly to those two enforcement modes: audit-mode runs out-of-band for full policy evaluation, while enforce-mode sits in the critical request path and must return a verdict before the downstream model call proceeds.

---

## Run it

```bash
docker compose up --build
# API: http://localhost:8000
# Interactive docs: http://localhost:8000/docs
```

Run tests:

```bash
make install
make test
```

Verify the live service against the running container:

```bash
bash scripts/smoke_test.sh
# Runs 9 checks including a latency benchmark — all should PASS
```

---

## API

Full OpenAPI spec at [`/docs`](http://localhost:8000/docs). Examples:

**`POST /detect`** — classify all matching topics

```bash
curl -s -X POST http://localhost:8000/detect \
  -H "Content-Type: application/json" \
  -d '{"prompt":"How would you suggest to treat depression?","settings":{"health":true,"finance":false,"hr":true,"legal":false}}'
# → {"detected_topics":["health"]}
```

**`POST /protect`** — return at least one match as fast as possible (inline enforcement)

```bash
curl -s -X POST http://localhost:8000/protect \
  -H "Content-Type: application/json" \
  -d '{"prompt":"A nurse negotiating her salary under a new employment contract","settings":{"health":true,"finance":false,"hr":true,"legal":true}}'
# → {"detected_topics":["hr"]}    # may be any one of the enabled topics that matches
```

**`GET /logs`** — audit trail of all calls

```bash
curl -s http://localhost:8000/logs | jq '.[0]'
# → {
#     "timestamp": "2026-05-02T14:11:26.139277Z",
#     "endpoint": "detect",
#     "prompt": "How would you suggest to treat depression?",
#     "detected_topics": ["health"]
#   }
```

Settings keys are always lowercase: `health`, `finance`, `legal`, `hr`.

---

## Design decisions

**1. Single LLM call per request over parallel per-topic calls.**
A single call that classifies all enabled topics at once is cheaper (one token budget per request) and simpler to reason about at this scope. The tradeoff is that `/protect` does not get a structural latency advantage over `/detect` — both make one classifier call, and measured response time is dominated by LLM variance rather than architecture. I attempted both prompt-level and model-level optimizations on `/protect`; neither moved the median because the latency floor is the proxy round-trip. See empirical latency. Parallel per-topic with `asyncio.as_completed()` is the correct next step for a real `/protect` SLO, but it multiplies cost by the number of enabled topics and belongs in a post-MVP iteration.

**2. Layered architecture: `classifiers/` isolated from `services/`, `services/` framework-agnostic.**
LLM I/O lives entirely in `src/classifiers/client.py`. Business logic in `src/services/` calls the two public classifier functions but never touches the OpenAI client directly. `services/` has no FastAPI imports — the HTTP layer is confined to `src/api/`. The tradeoff is one extra folder in a small codebase. The payoff: the LLM is an unreliable external dependency that this codebase is likely to swap (different model, different proxy, function-calling vs JSON mode). Isolating it behind two pure functions means the entire service layer is unit-testable without HTTP setup or live API calls, and any future LLM swap is contained to one file.

**3. JSON mode (`response_format=json_object`) with mandatory lowercase normalization.**
The spec explicitly warns that LLMs may not respond in the requested format. Requesting structured JSON output reduces parse failures. Every topic name returned by the model is lowercased and filtered against the known-valid set before it touches the API response or audit log — `"Health"` and `"HEALTH"` never reach the caller. The tradeoff is a slightly more constrained prompt format, which occasionally causes the model to be less expressive in edge cases. The alternative — parsing free text — would require fragile regex and would be the first thing to break in a demo.

**4. Fail-closed (HTTP 502) on classifier error over fail-open.**
When the LLM call fails — timeout, malformed JSON, proxy error — the service returns 502 rather than an empty topic list. For a security component, returning `{"detected_topics":[]}` on an error is a false negative: it tells the caller the prompt is safe when the system simply doesn't know. The tradeoff is that LLM outages propagate as errors to the caller, which must implement its own fallback policy (block-on-error vs allow-on-error). The service deliberately does not make that choice for the caller.

**5. Short-circuit when all topics are disabled.**
When the settings object has all topics set to false, the service returns an empty result immediately without calling the classifier. A disabled detection consuming a token budget is both a cost leak and a needless reliability risk: empty topic lists give the LLM no constraint and increase the chance of hallucinated output reaching the validator. The tradeoff is a subtle audit-log ambiguity: a log entry for an all-false request looks identical to one where the LLM found no matches, which can be confusing during debugging. Both cases correctly record the call with `detected_topics: []`.

**6. In-memory audit log over SQLite.**
The spec requires `/logs` but specifies nothing about durability or persistence across restarts. An in-memory Python list (`AuditStore`) satisfies the spec with zero dependencies. Adding SQLite would require SQLAlchemy async wiring, schema migrations, and introduces new failure modes (disk full, locked database) for no benefit in a single-process demo. The tradeoff is that the audit log is lost on container restart — which matters immediately in any real deployment.

### Empirical latency

The `/protect` endpoint went through two measurement-driven iterations:

**Iteration 0 (initial implementation):** `/protect` used a longer "fast" system prompt instructing the LLM to return early. Smoke testing showed `/protect` consistently slower than `/detect` — the input-token overhead exceeded the output-token savings.

**Iteration 1 (this build):** Aggressively shortened the `/protect` system prompt. The latency inversion was eliminated; endpoints are now roughly equivalent at the median.

**Iteration 2 (explored, not shipped):** Switched `/protect` to `gpt-4.1-mini` with `max_tokens=30`. Across 30 samples, the median was unchanged. Tail variance improved (~50% reduction in max), but the median did not move.

| Iteration | `/detect` median | `/protect` median |
|-----------|-----------------|------------------|
| 0 (longer prompt) | ~1100ms | ~1300ms |
| 1 (this build) | ~870ms | ~870ms |
| 2 (mini + cap) | ~870ms | ~870ms |

The conclusion is that median latency is bounded by the proxy round-trip (~800ms floor), not by the model or the prompt. To break the floor, the architecture must not wait for the LLM in the common case. Two paths, both documented in "What I'd do with more time": parallel per-topic with race-to-first-positive (true architectural fail-fast), or a hybrid with a local fast-path classifier for high-confidence prompts.

---

## What I'd do with more time

- **Parallel per-topic with race-to-first-positive for `/protect`.** Run one classifier call per enabled topic concurrently and return as soon as any task yields a match using `asyncio.as_completed()`. This gives `/protect` a genuine p50 latency advantage proportional to where in the topic list the first match appears. Cost: N × token spend per request. Worth it for a latency-SLO product.

- **Persistent audit store with pagination.** Replace the in-memory list with SQLite (or Postgres for multi-instance deployments). The current `/logs` endpoint returns the full log from the current process lifetime — useless for compliance or cross-restart debugging. Would also need cursor-based pagination; unbounded list responses don't scale.

- **Per-topic prompt templates.** The current classifier uses a single generic prompt for all four topics. Prompts tuned to each domain's vocabulary (clinical terminology for `health`, securities language for `finance`) would improve recall on edge cases and reduce false negatives from topic signal mixing in multi-topic prompts.

- **Authentication and tenant scoping.** Any caller can currently reach all endpoints. A real deployment would validate an API key per request, scope the audit log per tenant, and return 401 on unrecognised keys. This is the first thing to add before any production traffic.

- **Structured observability.** No metrics are emitted. The minimum for oncall monitoring would be Prometheus histograms for classifier latency per endpoint, a counter for 502s broken down by error type (timeout vs parse failure), and a liveness probe that validates the LLM proxy is reachable at startup.

---

## What I deliberately did not build

- **Authentication and multi-tenancy.** The spec doesn't require them. Adding a stub implementation would obscure the classification logic without testing anything real. In production, this service sits behind an authenticated API gateway that handles tenant isolation and API key validation before the request reaches the detection layer.

- **Retry logic on classifier failure.** Silently retrying a timed-out LLM call adds latency to an already time-critical path and can mask systematic proxy failures. The right retry policy (backoff, max attempts, circuit breaker) depends on the caller's SLO and belongs in the calling infrastructure, not in this service. The service's job is to tell the caller when it doesn't know — not to hide the failure.

- **Streaming responses.** `/protect` returns synchronously. An SSE variant that streams topic matches as they're detected would let callers block the moment the first topic arrives, without waiting for the full LLM response. This is the right architecture for true inline enforcement but requires a streaming-capable LLM call, which isn't meaningfully implementable within the single-call strategy.

---

## Repository layout

```
src/
  api/
    detection.py    /detect and /protect endpoints
    audit.py        /logs endpoint
    health.py       /health liveness check
  services/
    detection.py    detect() and protect() — orchestration, no FastAPI
    audit.py        AuditStore, get_audit_store Depends function
  classifiers/
    client.py       classify_all(), classify_fast(), _parse(), OpenAI client
  core/
    config.py       Settings via pydantic-settings (reads .env)
    logging.py      structlog configuration
    middleware.py   RequestIDMiddleware
  models/
    detection.py    Topic, DetectionSettings, PromptRequest, DetectionResult, AuditEntry
tests/
  unit/             Classifier decision boundary — OpenAI client mocked, no I/O
  integration/      End-to-end through the HTTP layer, classifier overridden via dependency_overrides
scripts/
  smoke_test.sh     Live-system test: 9 checks + latency benchmark (bash + curl + jq)
```

The one rule that must not break: `services/` and `classifiers/` never import from `api/` or from FastAPI. This is what makes the business logic unit-testable without an HTTP server.
