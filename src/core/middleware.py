import time
import uuid
from collections.abc import Awaitable, Callable

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

log = structlog.get_logger()


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Assign a request_id to every request and bind it to the log context.

    The id is read from the X-Request-Id header if present (so callers can
    correlate across services) or generated otherwise. It is echoed back on
    the response so clients can quote it in bug reports.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            path=request.url.path,
            method=request.method,
        )
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        log.info("request.complete", status=response.status_code, latency_ms=elapsed_ms)
        response.headers["x-request-id"] = request_id
        return response
