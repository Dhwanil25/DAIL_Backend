"""
Search API — unified full-text search across cases, documents, and opinions.

Uses PostgreSQL tsvector/tsquery for full-text search with ranking.
Designed to be swappable with Elasticsearch when scale demands it.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select, func, text, or_, case as sql_case
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.case import Case
from app.schemas.search import SearchRequest, SearchResponse, SearchHit

router = APIRouter()


@router.post("", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Full-text search across cases using PostgreSQL ts_rank.

    Supports keyword search with optional filters for jurisdiction,
    status, AI technology type, legal theory, and date ranges.
    Falls back to ILIKE when search vectors are not populated.
    """
    query = select(Case).where(Case.is_deleted == False)  # noqa: E712

    # ── Text search ──────────────────────────────────────────────────
    search_query = request.query.strip()
    if search_query:
        # Try tsvector search first, with ILIKE fallback
        ts_query = func.plainto_tsquery("english", search_query)
        query = query.where(
            or_(
                Case.search_vector.op("@@")(ts_query),
                Case.caption.ilike(f"%{search_query}%"),
                Case.brief_description.ilike(f"%{search_query}%"),
                Case.keywords.ilike(f"%{search_query}%"),
                Case.issue_text.ilike(f"%{search_query}%"),
                Case.algorithm_name.ilike(f"%{search_query}%"),
            )
        )

    # ── Filters ──────────────────────────────────────────────────────
    if request.jurisdiction:
        query = query.where(Case.jurisdiction_name.ilike(f"%{request.jurisdiction}%"))
    if request.jurisdiction_type:
        query = query.where(Case.jurisdiction_type == request.jurisdiction_type)
    if request.status:
        query = query.where(Case.status_disposition == request.status)
    if request.area_of_application:
        query = query.where(Case.area_of_application.ilike(f"%{request.area_of_application}%"))
    if request.class_action is not None:
        query = query.where(Case.class_action.ilike(f"%{request.class_action}%"))
    if request.date_filed_from:
        query = query.where(Case.filed_date >= request.date_filed_from)
    if request.date_filed_to:
        query = query.where(Case.filed_date <= request.date_filed_to)

    # JSONB array filters for AI technology type / legal theory / industry sector
    if request.ai_technology_type:
        query = query.where(
            Case.ai_technology_types.op("@>")(f'["{request.ai_technology_type}"]')
        )
    if request.legal_theory:
        query = query.where(
            Case.legal_theories.op("@>")(f'["{request.legal_theory}"]')
        )
    if request.industry_sector:
        query = query.where(
            Case.industry_sectors.op("@>")(f'["{request.industry_sector}"]')
        )

    # ── Count ────────────────────────────────────────────────────────
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    # ── Sort ─────────────────────────────────────────────────────────
    if request.sort_by == "date_filed":
        sort_col = Case.filed_date
    elif request.sort_by == "date_added":
        sort_col = Case.created_at
    elif request.sort_by == "caption":
        sort_col = Case.caption
    else:
        sort_col = Case.created_at  # Default for relevance

    if request.sort_order == "asc":
        query = query.order_by(sort_col.asc().nullslast())
    else:
        query = query.order_by(sort_col.desc().nullslast())

    # ── Paginate ─────────────────────────────────────────────────────
    offset = (request.page - 1) * request.page_size
    query = query.offset(offset).limit(request.page_size)

    result = await db.execute(query)
    cases = result.scalars().all()

    # ── Build response ───────────────────────────────────────────────
    hits = []
    for c in cases:
        snippet = None
        if c.brief_description:
            snippet = c.brief_description[:300]
        elif c.summary_of_facts:
            snippet = c.summary_of_facts[:300]

        hits.append(
            SearchHit(
                id=c.id,
                entity_type="case",
                title=c.caption,
                snippet=snippet,
                relevance_score=1.0,
                jurisdiction=c.jurisdiction_name,
                date_filed=c.filed_date,
                status=c.status_disposition,
                area_of_application=c.area_of_application,
            )
        )

    # ── Facets (aggregated counts) ───────────────────────────────────
    facets = await _build_facets(db)

    total_pages = max(1, (total + request.page_size - 1) // request.page_size)

    return SearchResponse(
        query=request.query,
        total=total,
        page=request.page,
        page_size=request.page_size,
        total_pages=total_pages,
        results=hits,
        facets=facets,
    )


async def _build_facets(db: AsyncSession) -> dict:
    """Build faceted counts for the search sidebar."""
    facets = {}

    # Status counts
    status_result = await db.execute(
        select(Case.status_disposition, func.count())
        .where(Case.is_deleted == False)  # noqa: E712
        .group_by(Case.status_disposition)
    )
    facets["status"] = {str(row[0]) if row[0] else "unknown": row[1] for row in status_result.all()}

    # Jurisdiction type counts
    jt_result = await db.execute(
        select(Case.jurisdiction_type, func.count())
        .where(Case.is_deleted == False, Case.jurisdiction_type.isnot(None))  # noqa: E712
        .group_by(Case.jurisdiction_type)
    )
    facets["jurisdiction_type"] = {row[0]: row[1] for row in jt_result.all()}

    # Area of application counts
    area_result = await db.execute(
        select(Case.area_of_application, func.count())
        .where(Case.is_deleted == False, Case.area_of_application.isnot(None))  # noqa: E712
        .group_by(Case.area_of_application)
    )
    facets["area_of_application"] = {row[0]: row[1] for row in area_result.all()}

    return facets
