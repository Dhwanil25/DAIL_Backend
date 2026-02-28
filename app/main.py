"""
DAIL Backend - FastAPI Application Entry Point

Configures and launches the DAIL REST API with middleware,
routers, startup/shutdown events, and OpenAPI documentation.
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

import redis.asyncio as aioredis
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.config import get_settings
from app.api.v1.router import api_router
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.audit import AuditMiddleware

settings = get_settings()
logger = structlog.get_logger()

# ── Redis client (shared across the app) ─────────────────────────────────
redis_client: aioredis.Redis | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown."""
    global redis_client

    # Startup
    logger.info("Starting DAIL Backend", env=settings.APP_ENV)
    try:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
        await redis_client.ping()
        logger.info("Redis connected")
    except Exception as e:
        logger.warning("Redis unavailable, caching disabled", error=str(e))
        redis_client = None

    app.state.redis = redis_client

    yield

    # Shutdown
    if redis_client:
        await redis_client.close()
    logger.info("DAIL Backend shutdown complete")


def create_application() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title="Database of AI Litigation (DAIL) API",
        description=(
            "A modern REST API for the Database of AI Litigation — "
            "cataloging litigation involving artificial intelligence technologies. "
            "Tracks cases from complaint forward across federal, state, and international jurisdictions."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
        contact={
            "name": "GW Law - Ethical Technology Initiative",
            "url": "https://blogs.gwu.edu/law-eti/",
        },
    )

    # ── Middleware (order matters: last added = first executed) ───────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(AuditMiddleware)
    app.add_middleware(RateLimitMiddleware)

    # ── Routers ──────────────────────────────────────────────────────
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_application()
