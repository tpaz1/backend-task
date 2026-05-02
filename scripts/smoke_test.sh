#!/usr/bin/env bash
# Smoke test for the Aim Prompt Guardrail API.
# Requires: curl, jq
# Usage: BASE_URL=http://localhost:8000 bash scripts/smoke_test.sh
set -uo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
PASS=0
FAIL=0

# ── Helpers ───────────────────────────────────────────────────────────────────

pass() { printf "  PASS  %s\n" "$1"; PASS=$((PASS + 1)); }
fail() { printf "  FAIL  %s\n" "$1"; FAIL=$((FAIL + 1)); }

assert_eq() {
  local label="$1" got="$2" want="$3"
  if [[ "$got" == "$want" ]]; then
    pass "$label"
  else
    fail "$label — got '$got', want '$want'"
  fi
}

assert_4xx() {
  local label="$1" status="$2"
  if [[ "$status" =~ ^4 ]]; then
    pass "$label (HTTP $status)"
  else
    fail "$label — got HTTP $status, want 4xx"
  fi
}

to_ms() {
  echo "$1" | awk '{printf "%.0f", $1 * 1000}'
}

detect() {
  curl -s -X POST "$BASE_URL/detect" -H "Content-Type: application/json" -d "$1"
}

protect() {
  curl -s -X POST "$BASE_URL/protect" -H "Content-Type: application/json" -d "$1"
}

MULTI='{"prompt":"A nurse negotiating her salary while reviewing her employment contract","settings":{"health":true,"finance":false,"hr":true,"legal":true}}'

echo "======================================================"
echo "  Aim Prompt Guardrail — smoke test"
echo "  Target: $BASE_URL"
echo "======================================================"
echo ""

# ── 0. Container reachability (fatal) ─────────────────────────────────────────
echo "── 0. Container reachability"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health" 2>/dev/null || echo "000")
if [[ "$STATUS" != "200" ]]; then
  echo ""
  echo "  FATAL: /health returned HTTP $STATUS — container is not running."
  echo "  Start it with: docker compose up -d"
  exit 1
fi
pass "/health reachable"
echo ""

# Record how many log entries already exist before our test calls.
LOG_OFFSET=$(curl -s "$BASE_URL/logs" | jq 'length')

# ── 1. /detect — spec example ─────────────────────────────────────────────────
echo "── 1. /detect spec example"
BODY=$(detect '{"prompt":"How would you suggest to treat depression?","settings":{"health":true,"finance":false,"hr":true,"legal":false}}')
assert_eq "spec example returns health" \
  "$(echo "$BODY" | jq -c .)" \
  '{"detected_topics":["health"]}'
echo ""

# ── 2. /detect — multi-topic prompt ───────────────────────────────────────────
echo "── 2. /detect multi-topic (expect >1 detected topic)"
BODY=$(detect "$MULTI")
COUNT=$(echo "$BODY" | jq '.detected_topics | length')
if [[ "$COUNT" -gt 1 ]]; then
  pass "multi-topic returns $COUNT topics: $(echo "$BODY" | jq -c .detected_topics)"
else
  fail "multi-topic returned only $COUNT topic(s) — got $(echo "$BODY" | jq -c .detected_topics)"
fi
echo ""

# ── 3. /detect — all-false settings ───────────────────────────────────────────
echo "── 3. /detect all-false settings (short-circuit, no LLM call)"
BODY=$(detect '{"prompt":"How do I treat depression?","settings":{"health":false,"finance":false,"hr":false,"legal":false}}')
assert_eq "all-false returns empty list" \
  "$(echo "$BODY" | jq -c .)" \
  '{"detected_topics":[]}'
echo ""

# ── 4. /detect — no-topic match ───────────────────────────────────────────────
echo "── 4. /detect no-match prompt (expect empty list)"
BODY=$(detect '{"prompt":"What is the capital of France?","settings":{"health":true,"finance":true,"hr":true,"legal":true}}')
assert_eq "off-topic prompt returns empty list" \
  "$(echo "$BODY" | jq -c .)" \
  '{"detected_topics":[]}'
echo ""

# ── 5. /protect — multi-topic prompt ──────────────────────────────────────────
echo "── 5. /protect multi-topic (expect exactly 1 topic)"
BODY=$(protect "$MULTI")
COUNT=$(echo "$BODY" | jq '.detected_topics | length')
assert_eq "protect returns exactly 1 topic (got: $(echo "$BODY" | jq -c .detected_topics))" \
  "$COUNT" "1"
echo ""

# ── 6. /logs audit trail ──────────────────────────────────────────────────────
echo "── 6. /logs audit trail"
LOGS=$(curl -s "$BASE_URL/logs")
TOTAL=$(echo "$LOGS" | jq 'length')
NEW=$((TOTAL - LOG_OFFSET))
assert_eq "logs gained exactly 5 new entries" "$NEW" "5"

EXPECTED_ENDPOINTS=("detect" "detect" "detect" "detect" "protect")
for i in 0 1 2 3 4; do
  IDX=$((LOG_OFFSET + i))
  EP=$(echo "$LOGS" | jq -r ".[$IDX].endpoint")
  assert_eq "logs[$IDX].endpoint" "$EP" "${EXPECTED_ENDPOINTS[$i]}"

  TS=$(echo "$LOGS" | jq -r ".[$IDX].timestamp")
  if [[ -n "$TS" && "$TS" != "null" ]]; then
    pass "logs[$IDX].timestamp present ($TS)"
  else
    fail "logs[$IDX].timestamp missing or null"
  fi
done
echo ""

# ── 7. Latency benchmark ──────────────────────────────────────────────────────
echo "── 7. Latency benchmark (5 × /detect, 5 × /protect, same multi-topic prompt)"
DETECT_TIMES=()
for i in $(seq 1 5); do
  T=$(curl -s -o /dev/null -w "%{time_total}" -X POST "$BASE_URL/detect" \
    -H "Content-Type: application/json" -d "$MULTI")
  DETECT_TIMES+=("$T")
  printf "  /detect  run %d: %sms\n" "$i" "$(to_ms "$T")"
done

PROTECT_TIMES=()
for i in $(seq 1 5); do
  T=$(curl -s -o /dev/null -w "%{time_total}" -X POST "$BASE_URL/protect" \
    -H "Content-Type: application/json" -d "$MULTI")
  PROTECT_TIMES+=("$T")
  printf "  /protect run %d: %sms\n" "$i" "$(to_ms "$T")"
done

IFS=$'\n'
SD=($(printf '%s\n' "${DETECT_TIMES[@]}"  | sort -g))
SP=($(printf '%s\n' "${PROTECT_TIMES[@]}" | sort -g))
unset IFS

echo ""
echo "  +----------------+-------------+--------------+-------------+"
echo "  | Endpoint       | min (ms)    | median (ms)  | max (ms)    |"
echo "  +----------------+-------------+--------------+-------------+"
printf "  | /detect        | %-11s | %-12s | %-11s |\n" \
  "$(to_ms "${SD[0]}")" "$(to_ms "${SD[2]}")" "$(to_ms "${SD[4]}")"
printf "  | /protect       | %-11s | %-12s | %-11s |\n" \
  "$(to_ms "${SP[0]}")" "$(to_ms "${SP[2]}")" "$(to_ms "${SP[4]}")"
echo "  +----------------+-------------+--------------+-------------+"
echo ""

# ── 8. Fail-closed: bad input shape ───────────────────────────────────────────
echo "── 8. Fail-closed: malformed request (missing required field)"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/detect" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"test prompt"}')
assert_4xx "missing 'settings' field returns 4xx" "$STATUS"
echo ""

# ── Summary ───────────────────────────────────────────────────────────────────
TOTAL=$((PASS + FAIL))
echo "======================================================"
printf "  %d/%d passed   %d failed\n" "$PASS" "$TOTAL" "$FAIL"
echo "======================================================"

[[ "$FAIL" -eq 0 ]]
