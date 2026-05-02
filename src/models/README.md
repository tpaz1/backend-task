# src/models/

Pydantic domain types shared across all layers. No logic lives here — only type definitions.

## detection.py

- **`Topic`** — `StrEnum` of the four valid topic keys: `health`, `finance`, `legal`, `hr`.
- **`DetectionSettings`** — Per-request on/off flags for each topic; all default to `false`.
- **`PromptRequest`** — The request body for `/detect` and `/protect`: a `prompt` string and a `DetectionSettings`.
- **`DetectionResult`** — The response body: a `detected_topics` list of strings.
- **`AuditEntry`** — A single audit log record: UTC `timestamp`, `endpoint` name, `prompt`, and `detected_topics`.

---

[← src/](../README.md) · [← Root README](../../README.md)
