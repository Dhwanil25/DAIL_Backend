"""
Search schemas — request/response models for the unified search endpoint.
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Unified search request across cases, documents, and opinions."""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query text")
    search_type: str = Field(
        "cases", description="Search domain: cases, documents, opinions, all"
    )

    # ── Filters ──────────────────────────────────────────────────────
    jurisdiction: Optional[str] = None
    jurisdiction_type: Optional[str] = None
    status: Optional[str] = None
    area_of_application: Optional[str] = None
    ai_technology_type: Optional[str] = None
    legal_theory: Optional[str] = None
    industry_sector: Optional[str] = None
    is_class_action: Optional[bool] = None

    # ── Date Filters ─────────────────────────────────────────────────
    date_filed_from: Optional[date] = None
    date_filed_to: Optional[date] = None

    # ── Pagination ───────────────────────────────────────────────────
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

    # ── Sort ─────────────────────────────────────────────────────────
    sort_by: str = Field("relevance", description="relevance, date_filed, date_added, caption")
    sort_order: str = Field("desc", pattern="^(asc|desc)$")


class SearchHit(BaseModel):
    """A single search result with relevance scoring."""
    id: int
    entity_type: str = Field(description="case, document, or opinion")
    title: str
    snippet: Optional[str] = Field(None, description="Highlighted text excerpt")
    relevance_score: float = 0.0

    # Case-specific fields
    jurisdiction: Optional[str] = None
    date_filed: Optional[date] = None
    status: Optional[str] = None
    area_of_application: Optional[str] = None


class SearchResponse(BaseModel):
    """Search response with results and faceted counts."""
    query: str
    total: int
    page: int
    page_size: int
    total_pages: int
    results: list[SearchHit]

    # ── Facets ───────────────────────────────────────────────────────
    facets: Optional[dict] = Field(
        None,
        description="Aggregated counts by jurisdiction, status, technology type, etc."
    )


class AnalyticsSummary(BaseModel):
    """Database-wide analytics and statistics."""
    total_cases: int = 0
    total_documents: int = 0
    total_opinions: int = 0
    total_citations: int = 0
    total_parties: int = 0
    total_courts: int = 0

    cases_by_status: dict[str, int] = {}
    cases_by_jurisdiction_type: dict[str, int] = {}
    cases_by_area_of_application: dict[str, int] = {}
    cases_by_ai_technology_type: dict[str, int] = {}
    cases_by_legal_theory: dict[str, int] = {}
    cases_by_year: dict[str, int] = {}

    recent_cases: list[dict] = []
    most_active_jurisdictions: list[dict] = []
