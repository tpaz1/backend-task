---
name: python-api-conventions
description: This skill should be used whenever writing FastAPI code in this project — creating routers, services, Pydantic models, dependency injection, exception handlers, or any HTTP-layer code. It defines the layered architecture (api/services/core), the rule that services never import FastAPI, request/response/domain model conventions, async vs sync defaults, and error response shape. Claude must consult this skill before writing any new endpoint, service method, or restructuring the src/ directory.
---

# Python API Conventions

Patterns that apply to any FastAPI backend, regardless of what the service
does.

## Layered structure

Three default layers:

```
src/
  api/      HTTP routers. Thin. No business logic.
  services/ Business logic. Pure functions where possible. No FastAPI.
  core/     Config, logging, middleware, shared infrastructure.
```

Add more folders only when there's a clear domain reason (the bootstrap skill
will identify these).

## Routers are thin

A router does four things and nothing more:
1. Parse and validate request (Pydantic does this)
2. Call a service method
3. Translate exceptions to HTTP errors
4. Return the result (Pydantic serializes)

If a router has business logic, move it to a service.

```python
# Good
@router.post("/items")
async def create_item(req: CreateItemRequest, svc: ItemService = Depends(...)):
    item = await svc.create(req.name, req.value)
    return ItemResponse.from_domain(item)

# Bad — business logic in the router
@router.post("/items")
async def create_item(req: CreateItemRequest):
    if req.value < 0:
        raise HTTPException(400, "value must be non-negative")
    # ... validation, persistence, side effects all here
```

## Services don't import FastAPI

Services raise domain exceptions (`ItemNotFound`, `InvalidPolicy`). The API
layer translates those to HTTP errors via exception handlers in `main.py`:

```python
@app.exception_handler(ItemNotFound)
async def item_not_found(request: Request, exc: ItemNotFound):
    return JSONResponse(status_code=404, content={"error": str(exc)})
```

This is what makes services unit-testable without spinning up an HTTP client.

## Pydantic models — three flavors

Keep these distinct in your head:

- **Request models** (`CreateItemRequest`) — what callers send. Validated.
- **Response models** (`ItemResponse`) — what callers receive. May omit
  internal fields.
- **Domain models** (`Item`) — the business object. Used inside services.

For a small assignment it's fine to use the same Pydantic model for all
three, but be aware of when you should split (e.g. when responses must hide
fields like `internal_id` or `password_hash`).

## Dependency injection

Use FastAPI's `Depends()` for dependencies that have lifecycle (DB sessions,
HTTP clients) or for things you want to override in tests (the most common
override target is "fake the upstream LLM" or "fake the database").

```python
def get_service() -> ItemService:
    return ItemService(repo=get_repo())

@router.get("/items/{id}")
async def get_item(id: str, svc: ItemService = Depends(get_service)):
    return await svc.get(id)

# in tests:
app.dependency_overrides[get_service] = lambda: FakeItemService()
```

## Async or sync

Default to async for I/O-bound work (DB, HTTP, file). Sync is fine for pure
computation. Don't mix — calling sync blocking code from an async handler
without `run_in_executor` is a foot-gun. If the assignment is mostly CPU
work (parsing, classification), sync is the simpler choice.

## Error responses

Use a consistent shape across the API:

```json
{ "error": "human readable", "code": "machine_readable" }
```

Map domain exceptions to status codes in one place (an exception handler
module). This is cheap to set up and looks much more polished than raw
HTTPException scattered around.

## Health endpoint

Always include `/health`. It's free and demonstrates ops-awareness.
