from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api import health
from src.api import detection, audit
from src.core.config import settings
from src.core.logging import configure_logging
from src.core.middleware import RequestIDMiddleware

log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(json_logs=settings.log_json, level=settings.log_level)
    log.info("app.startup", env=settings.env)
    yield
    log.info("app.shutdown")


app = FastAPI(
    title="Aim Prompt Guardrail",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(RequestIDMiddleware)
app.include_router(health.router)
app.include_router(detection.router)
app.include_router(audit.router)


@app.exception_handler(ValueError)
async def classifier_error_handler(_: Request, exc: ValueError) -> JSONResponse:
    log.warning("classifier.parse_error", detail=str(exc))
    return JSONResponse(status_code=502, content={"detail": "Classifier returned an unparseable response"})
