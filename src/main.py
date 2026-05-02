from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from src.api import health
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
    title="Cato Take-home",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(RequestIDMiddleware)
app.include_router(health.router)
