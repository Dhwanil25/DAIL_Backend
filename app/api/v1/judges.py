"""
Judges API — CRUD endpoints for judges.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import PaginationDep, require_api_key
from app.models.judge import Judge
from app.schemas.judge import JudgeCreate, JudgeUpdate, JudgeResponse
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse[JudgeResponse])
async def list_judges(
    pagination: PaginationDep = Depends(),
    db: AsyncSession = Depends(get_db),
    search: Optional[str] = Query(None, description="Search judge name"),
    court: Optional[str] = Query(None, description="Filter by court"),
):
    """List judges with optional filtering."""
    query = select(Judge).where(Judge.is_alias == False)  # noqa: E712

    if search:
        query = query.where(Judge.name.ilike(f"%{search}%"))
    if court:
        query = query.where(Judge.court_name.ilike(f"%{court}%"))

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    query = query.order_by(Judge.name).offset(pagination.offset).limit(pagination.page_size)
    result = await db.execute(query)
    judges = result.scalars().all()

    return PaginatedResponse.create(
        items=[JudgeResponse.model_validate(j) for j in judges],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get("/{judge_id}", response_model=JudgeResponse)
async def get_judge(judge_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single judge by ID."""
    result = await db.execute(select(Judge).where(Judge.id == judge_id))
    judge = result.scalar_one_or_none()
    if not judge:
        raise HTTPException(status_code=404, detail=f"Judge {judge_id} not found")
    return JudgeResponse.model_validate(judge)


@router.post("", response_model=JudgeResponse, status_code=201)
async def create_judge(
    judge_in: JudgeCreate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(require_api_key),
):
    """Create a new judge. Requires API key."""
    judge = Judge(**judge_in.model_dump())
    db.add(judge)
    await db.flush()
    await db.refresh(judge)
    return JudgeResponse.model_validate(judge)


@router.patch("/{judge_id}", response_model=JudgeResponse)
async def update_judge(
    judge_id: int,
    judge_in: JudgeUpdate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(require_api_key),
):
    """Update a judge. Requires API key."""
    result = await db.execute(select(Judge).where(Judge.id == judge_id))
    judge = result.scalar_one_or_none()
    if not judge:
        raise HTTPException(status_code=404, detail=f"Judge {judge_id} not found")

    for field, value in judge_in.model_dump(exclude_unset=True).items():
        setattr(judge, field, value)

    await db.flush()
    await db.refresh(judge)
    return JudgeResponse.model_validate(judge)
