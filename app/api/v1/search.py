"""Full-text and filtered search endpoint."""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.case import Case
from app.schemas.case import CaseResponse
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=PaginatedResponse[CaseResponse])
async def search_cases(
    q: str = Query(..., min_length=1, description="Search query"),
    status: Optional[str] = None,
    jurisdiction_type: Optional[str] = None,
    area_of_application: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Full-text search across cases with optional field filters.

    The ``q`` parameter is run against the PostgreSQL tsvector index
    (weighted: caption > description/keyword > issues/orgs > summaries).
    """
    ts_query = func.plainto_tsquery("english", q)
    stmt = select(Case).where(Case.search_vector.op("@@")(ts_query))

    if status:
        stmt = stmt.where(Case.status_disposition.ilike(f"%{status}%"))
    if jurisdiction_type:
        stmt = stmt.where(Case.jurisdiction_type.ilike(f"%{jurisdiction_type}%"))
    if area_of_application:
        stmt = stmt.where(Case.area_of_application.ilike(f"%{area_of_application}%"))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    # Rank by relevance
    rank = func.ts_rank_cd(Case.search_vector, ts_query)
    stmt = stmt.order_by(rank.desc()).offset(skip).limit(limit)
    rows = (await db.execute(stmt)).scalars().all()

    return PaginatedResponse(items=rows, total=total, skip=skip, limit=limit)
