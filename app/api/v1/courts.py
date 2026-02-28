"""
Courts API — CRUD endpoints for courts.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import PaginationDep, require_api_key
from app.models.court import Court
from app.schemas.court import CourtCreate, CourtUpdate, CourtResponse
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse[CourtResponse])
async def list_courts(
    pagination: PaginationDep = Depends(),
    db: AsyncSession = Depends(get_db),
    jurisdiction_type: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    search: Optional[str] = Query(None, description="Search court name"),
):
    """List all courts with optional filtering."""
    query = select(Court)

    if jurisdiction_type:
        query = query.where(Court.jurisdiction_type == jurisdiction_type)
    if state:
        query = query.where(Court.state.ilike(f"%{state}%"))
    if search:
        query = query.where(Court.name.ilike(f"%{search}%"))

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    query = query.order_by(Court.name).offset(pagination.offset).limit(pagination.page_size)
    result = await db.execute(query)
    courts = result.scalars().all()

    return PaginatedResponse.create(
        items=[CourtResponse.model_validate(c) for c in courts],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get("/{court_id}", response_model=CourtResponse)
async def get_court(court_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single court by ID."""
    result = await db.execute(select(Court).where(Court.id == court_id))
    court = result.scalar_one_or_none()
    if not court:
        raise HTTPException(status_code=404, detail=f"Court {court_id} not found")
    return CourtResponse.model_validate(court)


@router.post("", response_model=CourtResponse, status_code=201)
async def create_court(
    court_in: CourtCreate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(require_api_key),
):
    """Create a new court. Requires API key."""
    court = Court(**court_in.model_dump())
    db.add(court)
    await db.flush()
    await db.refresh(court)
    return CourtResponse.model_validate(court)


@router.patch("/{court_id}", response_model=CourtResponse)
async def update_court(
    court_id: int,
    court_in: CourtUpdate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(require_api_key),
):
    """Update a court. Requires API key."""
    result = await db.execute(select(Court).where(Court.id == court_id))
    court = result.scalar_one_or_none()
    if not court:
        raise HTTPException(status_code=404, detail=f"Court {court_id} not found")

    for field, value in court_in.model_dump(exclude_unset=True).items():
        setattr(court, field, value)

    await db.flush()
    await db.refresh(court)
    return CourtResponse.model_validate(court)
