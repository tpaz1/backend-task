# postman/

## Using the collection

Import `aim-prompt-guardrail.postman_collection.json` into Postman. The collection has one variable, `baseUrl`, defaulting to `http://localhost:8000` — update it if the service is running elsewhere. Run requests individually to explore the API, or use Collection Runner to execute all four in sequence. Each request includes assertion tests that verify status 200 and the expected response shape; they pass when the container is running and healthy.

The four requests cover: liveness (`/health`), the canonical spec example (`/detect`), the fail-fast single-topic path (`/protect`), and the audit trail (`/logs`).

---

[← Root README](../README.md)
