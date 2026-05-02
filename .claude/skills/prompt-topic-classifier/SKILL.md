---
name: prompt-topic-classifier
description: This skill should be used whenever writing any code for the prompt topic-detection service in this project — the /detect endpoint, the /protect endpoint, the /logs endpoint, the classifier logic, the OpenAI proxy integration, or the audit store. It defines the domain vocabulary (prompt, topic, classification, detect vs protect, inline guardrail, audit), the wire-format invariant (lowercase keys everywhere), the core abstractions (PromptRequest, DetectionSettings, DetectionResult, AuditEntry, Topic), the key architectural tension between /detect (complete) and /protect (fail-fast), and the table-driven test pattern for the classifier decision boundary. Claude must consult this skill before writing any classifier prompt, any endpoint handler, any OpenAI call, or any README design-decisions section.
---

## 1. What this is

A topic-detection service that acts as an inline guardrail for GenAI pipelines. It receives a user prompt and a policy settings object, calls an LLM (GPT-4.1 via the Aim proxy) to classify which sensitive topics the prompt touches, and returns the result. Two detection modes exist: `/detect` returns the **complete** list of matched topics; `/protect` is the fail-fast variant that returns **at least one** matched topic as quickly as possible, optimised for time-critical inline enforcement. Every call is written to an in-memory audit log exposed by `/logs`.

---

## 2. Domain vocabulary

- **prompt** — the raw text submitted by the end-user to a downstream LLM, to be inspected before forwarding
- **topic** — a sensitive domain category: `health`, `finance`, `legal`, `hr` (always lowercase, matching the spec's JSON keys)
- **classification** — the act of deciding which topics a prompt touches, performed by the LLM classifier
- **settings** — a per-request policy object specifying which topics are enabled for detection (`{"health": true, "finance": false, ...}`)
- **detect** — complete-mode endpoint; waits for all enabled topics to be evaluated before responding
- **protect** — fail-fast endpoint; returns as soon as at least one topic is confirmed; used for inline pipeline protection
- **inline guardrail** — enforcement that sits in the request path and must not add perceptible latency; this is what `/protect` serves
- **audit** — immutable append-only record of every call: timestamp, endpoint (detect/protect), prompt, and result
- **detected_topics** — the response field: a list of matched topic strings (empty list = no match)
- **Aim proxy** — the OpenAI-compatible endpoint at `https://api.aim.security/fw/v1/proxy/openai` used instead of the public OpenAI API

**Wire-format invariant:** the API contract uses lowercase keys (`health`, `finance`, `legal`, `hr`) in settings input, `detected_topics` response, and audit entries. The LLM may return capitalized or mixed-case variants — normalize all topic strings to lowercase before they touch any response or audit record. LLM-capitalized variants must never leak into the API contract.

---

## 3. Core abstractions

**DetectionSettings** — which topics are active for this request.
Fields: `health: bool`, `finance: bool`, `legal: bool`, `hr: bool`

**PromptRequest** — the body accepted by `/detect` and `/protect`.
Fields: `prompt: str`, `settings: DetectionSettings`

**DetectionResult** — the response returned by `/detect` and `/protect`.
Fields: `detected_topics: list[str]`

**AuditEntry** — one record in the audit log.
Fields: `timestamp: datetime`, `endpoint: str` ("detect" | "protect"), `prompt: str`, `detected_topics: list[str]`

**Topic** — string enum with values `health`, `finance`, `legal`, `hr`. Used to avoid magic strings throughout the classifier.

---

## 4. Folder layout addition

Add `src/classifiers/` — contains the LLM classifier logic: the prompt template, the OpenAI client wrapper, the response parser, and the classify functions. Keeps LLM I/O out of the service layer and makes it testable by swapping the client.

The default `api/`, `services/`, `core/` layout handles the rest. No second addition needed.

---

## 5. Key tradeoffs

**1. Single LLM call (all topics) vs parallel per-topic calls**
For this build, a single LLM call that classifies all enabled topics at once is the default strategy. It is cheaper (one round-trip, one token budget), simpler to implement, and sufficient for the 3-hour scope. Parallel per-topic calls — racing them with `asyncio.as_completed()` so `/protect` can return the first positive result — are the natural next step if latency SLOs demand it, but they multiply API cost by the number of enabled topics and add coordination complexity. Deferred.

**2. /detect completeness vs /protect speed**
Within the single-call strategy, the `/detect` vs `/protect` distinction is implemented primarily through **prompt biasing**: `/protect`'s system prompt instructs the LLM to report the first match it finds rather than exhaustively listing all matches, reducing the reasoning work per call. This is honest about the 3-hour scope: both endpoints share the same call path; the speed difference comes from how the LLM is asked to respond, not from architectural parallelism. The README should name this explicitly as the tradeoff made.

**3. Structured output (JSON mode) vs free-text parsing**
Asking the LLM to respond in JSON (via `response_format={"type": "json_object"}`) reduces parse failures at the cost of slightly more prompt engineering. Free-text is simpler to prompt but requires fragile string parsing. The spec explicitly warns about format failures — use JSON mode.

**4. In-memory audit log vs SQLite persistence**
The spec requires `/logs` but says nothing about durability. An in-memory Python list meets the spec with zero configuration. SQLite adds durability and restartability but would need SQLAlchemy wiring. Use in-memory; call out the tradeoff in the README.

**5. Fail-open vs fail-closed on LLM error**
If the GPT call fails (timeout, bad JSON, network error), we can either return an error to the caller (fail-closed — safest for a security product) or return an empty result (fail-open — keeps pipelines moving). For an inline guardrail, fail-closed is the correct default; return HTTP 502 so the caller knows classification did not succeed.

---

## 6. Test patterns

**Table-driven tests over the classifier decision boundary** — the right shape here. The core logic is: given a prompt and a settings object, which topics are returned? A table of `(prompt, settings, expected_topics)` rows covers: match on enabled topic, no match on disabled topic, multi-topic prompt, empty settings, all-topics-false, LLM format error. Each row is one assertion. Mock the OpenAI client to inject controlled LLM responses, keeping tests fast and deterministic without live API calls.

For endpoints: one integration test per endpoint (happy-path, using `httpx.AsyncClient` against the live app with the OpenAI client mocked) is enough.

---

## 7. What this is NOT

- Not a policy enforcement engine — the service **detects** topics and reports them; it does not block, redact, or modify the prompt. Enforcement is the caller's responsibility.
- Not a multi-model classifier — one LLM (GPT-4.1 via Aim proxy) only. No fallback models, no local classifiers.
- Not a persistent audit system — `/logs` returns in-memory state from the current process lifetime. No database, no search, no pagination required by the spec.
- Not a real-time streaming endpoint — `/protect` is fast but not SSE/WebSocket streaming. It returns a normal JSON response, just using a faster internal strategy.

---

## 8. Cato-flavored framing for the README

This service is a simplified version of the inline inspection layer inside Aim Security's AI Firewall (now part of Cato's AI Security product line). In production, the same detect/protect split maps directly to audit-mode vs enforcement-mode policy evaluation: detect runs out-of-band for full analysis, protect sits in the critical path and must return before the downstream LLM call proceeds.
