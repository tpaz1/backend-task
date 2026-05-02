# scripts/

## smoke_test.sh

Live-system test against the running container. Not part of `make test` — requires Docker and a live API key.

**Prerequisites:** container running (`docker compose up -d`), `curl`, `jq`.

**Invocation:**
```bash
bash scripts/smoke_test.sh
# or with a non-default target:
BASE_URL=http://localhost:8000 bash scripts/smoke_test.sh
```

**9 checks, 18 assertions total:**

1. Container reachability — `/health` returns 200 (fatal: aborts if this fails)
2. `/detect` spec example — exact match `{"detected_topics":["health"]}`
3. `/detect` multi-topic prompt — returns more than one topic
4. `/detect` all-false settings — short-circuit returns empty list without an LLM call
5. `/detect` off-topic prompt — returns empty list
6. `/protect` multi-topic prompt — returns exactly one topic
7. Audit log — `/logs` gained exactly 5 new entries with correct endpoints and timestamps
8. Latency benchmark — 5 runs each of `/detect` and `/protect`; prints min/median/max table
9. Fail-closed — malformed request (missing `settings`) returns 4xx

---

[← Root README](../README.md) · [tests/](../tests/README.md)
