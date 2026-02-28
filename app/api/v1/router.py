"""
API v1 Router — aggregates all v1 endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.cases import router as cases_router
from app.api.v1.courts import router as courts_router
from app.api.v1.dockets import router as dockets_router
from app.api.v1.opinions import router as opinions_router
from app.api.v1.citations import router as citations_router
from app.api.v1.parties import router as parties_router
from app.api.v1.judges import router as judges_router
from app.api.v1.documents import router as documents_router
from app.api.v1.secondary_sources import router as secondary_sources_router
from app.api.v1.search import router as search_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.courtlistener import router as courtlistener_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["Health"])
api_router.include_router(cases_router, prefix="/cases", tags=["Cases"])
api_router.include_router(courts_router, prefix="/courts", tags=["Courts"])
api_router.include_router(dockets_router, prefix="/dockets", tags=["Dockets"])
api_router.include_router(opinions_router, prefix="/opinions", tags=["Opinions"])
api_router.include_router(citations_router, prefix="/citations", tags=["Citations"])
api_router.include_router(parties_router, prefix="/parties", tags=["Parties"])
api_router.include_router(judges_router, prefix="/judges", tags=["Judges"])
api_router.include_router(documents_router, prefix="/documents", tags=["Documents"])
api_router.include_router(
    secondary_sources_router, prefix="/secondary-sources", tags=["Secondary Sources"]
)
api_router.include_router(search_router, prefix="/search", tags=["Search"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(
    courtlistener_router, prefix="/courtlistener", tags=["CourtListener"]
)
