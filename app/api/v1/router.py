"""Central v1 API router — registers all sub-routers."""

from fastapi import APIRouter

from app.api.v1 import (
    ai,
    analytics,
    cases,
    dockets,
    documents,
    health,
    search,
    secondary_sources,
)

router = APIRouter()

router.include_router(health.router)
router.include_router(cases.router)
router.include_router(dockets.router)
router.include_router(documents.router)
router.include_router(secondary_sources.router)
router.include_router(search.router)
router.include_router(analytics.router)
router.include_router(ai.router)
