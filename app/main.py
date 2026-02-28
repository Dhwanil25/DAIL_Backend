"""
DAIL Backend - FastAPI Application Entry Point

Modernising the Database of AI Litigation (DAIL).
Four-table PostgreSQL schema matching Caspio exports,
RESTful CRUD, full-text search, analytics dashboard,
and LLM-powered endpoints (GPT-4o + Gemini).
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.v1.router import router as v1_router

settings = get_settings()

# ── Logging ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("dail")


# ── Lifespan ─────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("DAIL Backend starting …")
    yield
    logger.info("DAIL Backend shutting down …")


# ── App ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="DAIL – Database of AI Litigation API",
    description=(
        "REST API for the Database of AI Litigation.  Provides CRUD access to "
        "four core tables (cases, dockets, documents, secondary sources), "
        "full-text search, analytics, and LLM-powered endpoints for natural-"
        "language querying (GPT-4o) and document image extraction (Gemini)."
    ),
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ─────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ───────────────────────────────────────────────────────────
app.include_router(v1_router, prefix=settings.API_V1_PREFIX)


@app.get("/", include_in_schema=False)
async def root():
    return {
        "service": "DAIL Backend",
        "version": "2.0.0",
        "docs": "/docs",
    }
