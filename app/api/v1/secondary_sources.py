"""
Secondary Sources API — CRUD endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import require_api_key
from app.models.secondary_source import SecondarySource
from app.schemas.secondary_source import (
    SecondarySourceCreate,
    SecondarySourceUpdate,
    SecondarySourceResponse,
)

router = APIRouter()


@router.get("/{source_id}", response_model=SecondarySourceResponse)
async def get_secondary_source(source_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single secondary source by ID."""
    result = await db.execute(select(SecondarySource).where(SecondarySource.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail=f"Secondary source {source_id} not found")
    return SecondarySourceResponse.model_validate(source)


@router.post("", response_model=SecondarySourceResponse, status_code=201)
async def create_secondary_source(
    source_in: SecondarySourceCreate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(require_api_key),
):
    """Create a new secondary source. Requires API key."""
    source = SecondarySource(**source_in.model_dump())
    db.add(source)
    await db.flush()
    await db.refresh(source)
    return SecondarySourceResponse.model_validate(source)


@router.patch("/{source_id}", response_model=SecondarySourceResponse)
async def update_secondary_source(
    source_id: int,
    source_in: SecondarySourceUpdate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(require_api_key),
):
    """Update a secondary source. Requires API key."""
    result = await db.execute(select(SecondarySource).where(SecondarySource.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail=f"Secondary source {source_id} not found")

    for field, value in source_in.model_dump(exclude_unset=True).items():
        setattr(source, field, value)

    await db.flush()
    await db.refresh(source)
    return SecondarySourceResponse.model_validate(source)


@router.delete("/{source_id}", status_code=204)
async def delete_secondary_source(
    source_id: int,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(require_api_key),
):
    """Delete a secondary source. Requires API key."""
    result = await db.execute(select(SecondarySource).where(SecondarySource.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail=f"Secondary source {source_id} not found")
    await db.delete(source)
