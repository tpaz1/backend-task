---
name: testing-patterns
description: This skill should be used whenever writing pytest tests in this project — unit tests, integration tests, fixtures, parametrized tests, or test fakes. It defines the two-tier strategy (unit for domain logic, integration for endpoints), table-driven test structure, naming conventions ("test names read as English sentences"), the httpx.AsyncClient + ASGITransport integration pattern, dependency overrides instead of mocks, and what NOT to test. Claude must consult this skill before writing any test file or adding test cases.
---

# Testing Patterns

How to write tests that look professional, document behavior, and survive a
code review.

## The two-tier strategy

For a 3-hour take-home, write tests at two levels:

1. **Unit tests** for the core domain logic. No I/O. Fast. Many cases,
   table-driven where possible.
2. **Integration tests** for the API. One happy-path test per endpoint, plus
   one error-path test for any non-trivial validation.

That's it. Don't write unit tests for routers (low signal). Don't write
integration tests for every edge case (slow, repetitive).

## Table-driven tests

The most defensible test shape for any logic with a clear input → output
mapping (classifiers, policies, parsers, evaluators):

```python
import pytest

@pytest.mark.parametrize("input_value, expected", [
    ("clean text", "allow"),
    ("contains_secret_keyword", "block"),
    ("4111-1111-1111-1111", "block"),
    ("", "allow"),  # edge case
])
def test_evaluator(input_value, expected):
    assert evaluate(input_value).verdict == expected
```

Why this is good:
- Each row documents one behavior
- Adding a case is one line
- A failure tells you exactly which case broke
- Reads as a specification

## Test names that read as sentences

```python
def test_returns_allow_for_clean_prompt(): ...
def test_returns_block_when_credit_card_present(): ...
def test_redacts_email_address_in_prompt(): ...
```

Not `test_evaluator_1`, not `test_basic_case`. The reviewer scrolls through
test names and sees a bullet list of what the system does.

## Integration tests with httpx.AsyncClient

```python
from httpx import ASGITransport, AsyncClient
from src.main import app

async def test_endpoint_happy_path():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/items", json={"name": "x", "value": 1})
    assert response.status_code == 201
    assert response.json()["name"] == "x"
```

No real network. No subprocess. Fast and deterministic.

## Faking dependencies

Don't mock. Override.

```python
class FakeUpstream:
    async def call(self, prompt: str) -> str:
        return "fake response"

def test_service_uses_upstream():
    svc = MyService(upstream=FakeUpstream())
    result = svc.process("hello")
    assert result == "fake response"
```

Or for FastAPI dependencies:

```python
app.dependency_overrides[get_upstream] = lambda: FakeUpstream()
```

Mocks (`unittest.mock`, `MagicMock`) are a code smell in 2026 Python — they
test that you called methods, not that the system behaves correctly. Override
real implementations with simple fakes.

## Fixtures

Use a `conftest.py` for shared fixtures. Keep fixtures small and obvious.
Don't build a fixture pyramid for a 3-hour assignment.

```python
# tests/conftest.py
import pytest
from src.main import app

@pytest.fixture
def test_app():
    return app
```

## What NOT to test

- Don't test that Pydantic validates fields (Pydantic's job)
- Don't test that FastAPI routes URLs (FastAPI's job)
- Don't test private helpers in isolation if they're already tested via the
  public function that calls them
- Don't write tests just for coverage — they're padding and reviewers can
  tell

## What to ALWAYS test

- The decision boundary of your core logic (every distinct outcome)
- Error paths your code explicitly handles
- One end-to-end happy path per endpoint

## Coverage

Don't aim for 100%. Aim for "every meaningful behavior has a test." For a
3-hour assignment, 70-85% coverage with a clear test list reads better than
100% with padding tests.
