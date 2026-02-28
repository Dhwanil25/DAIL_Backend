"""
Cases API — CRUD endpoints for AI litigation cases.

The core resource of the DAIL system.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.api.deps import PaginationDep, require_api_key
from app.models.case import Case
from app.models.docket import Docket
from app.models.document import Document
from app.models.secondary_source import SecondarySource
from app.models.ai_classification import AIClassification
from app.schemas.case import (
    CaseCreate,
    CaseUpdate,
    CaseResponse,
    CaseListResponse,
)
from app.schemas.common import PaginatedResponse, MessageResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse[CaseListResponse])
async def list_cases(
    pagination: PaginationDep = Depends(),
    db: AsyncSession = Depends(get_db),
    # Filters
    status: Optional[str] = Query(None, description="Filter by status_disposition"),
    jurisdiction: Optional[str] = Query(None, description="Filter by jurisdiction name"),
    jurisdiction_type: Optional[str] = Query(None, description="Filter by jurisdiction type"),
    area_of_application: Optional[str] = Query(None, description="Filter by area of application"),
    class_action: Optional[str] = Query(None, description="Filter class actions (Yes/No/Putative)"),
    keyword: Optional[str] = Query(None, description="Keyword search in caption and description"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort direction: asc or desc"),
):
    """
    List all cases with optional filtering and pagination.
    """
    query = select(Case).where(Case.is_deleted == False)  # noqa: E712

    # Apply filters
    if status:
        query = query.where(Case.status_disposition.ilike(f"%{status}%"))
    if jurisdiction:
        query = query.where(Case.jurisdiction_name.ilike(f"%{jurisdiction}%"))
    if jurisdiction_type:
        query = query.where(Case.jurisdiction_type == jurisdiction_type)
    if area_of_application:
        query = query.where(Case.area_of_application.ilike(f"%{area_of_application}%"))
    if class_action is not None:
        query = query.where(Case.class_action.ilike(f"%{class_action}%"))
    if keyword:
        query = query.where(
            or_(
                Case.caption.ilike(f"%{keyword}%"),
                Case.brief_description.ilike(f"%{keyword}%"),
                Case.keywords.ilike(f"%{keyword}%"),
                Case.issue_text.ilike(f"%{keyword}%"),
            )
        )

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    # Sort
    sort_column = getattr(Case, sort_by, Case.created_at)
    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # Paginate
    query = query.offset(pagination.offset).limit(pagination.page_size)
    result = await db.execute(query)
    cases = result.scalars().all()

    return PaginatedResponse.create(
        items=[CaseListResponse.model_validate(c) for c in cases],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(case_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a single case by ID with all related data (dockets, documents,
    secondary sources, classifications).
    """
    query = (
        select(Case)
        .options(
            selectinload(Case.dockets),
            selectinload(Case.documents),
            selectinload(Case.secondary_sources),
            selectinload(Case.ai_classifications),
            selectinload(Case.case_parties),
        )
        .where(Case.id == case_id, Case.is_deleted == False)  # noqa: E712
    )
    result = await db.execute(query)
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    return CaseResponse.model_validate(case)


@router.get("/record/{record_number}", response_model=CaseResponse)
async def get_case_by_record_number(
    record_number: str, db: AsyncSession = Depends(get_db)
):
    """
    Get a case by its legacy DAIL record number (Caspio ID).
    """
    query = (
        select(Case)
        .options(
            selectinload(Case.dockets),
            selectinload(Case.documents),
            selectinload(Case.secondary_sources),
            selectinload(Case.ai_classifications),
        )
        .where(Case.record_number == record_number, Case.is_deleted == False)  # noqa: E712
    )
    result = await db.execute(query)
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(
            status_code=404, detail=f"Case with record_number {record_number} not found"
        )

    return CaseResponse.model_validate(case)


@router.post("", response_model=CaseResponse, status_code=201)
async def create_case(
    case_in: CaseCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new case. Requires API key authentication.
    """
    # Check for duplicate record_number
    if case_in.record_number:
        existing = await db.execute(
            select(Case).where(Case.record_number == case_in.record_number)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=409,
                detail=f"Case with record_number {case_in.record_number} already exists",
            )

    data = case_in.model_dump(exclude_unset=True)

    # Auto-generate record_number if not supplied
    if not data.get("record_number"):
        from sqlalchemy import text as sa_text
        row = await db.execute(sa_text("SELECT nextval('cases_id_seq')"))
        next_id = row.scalar()
        data["record_number"] = f"DAIL-{next_id:04d}"
        # Reset sequence so the actual INSERT gets the same id
        await db.execute(sa_text(f"SELECT setval('cases_id_seq', {next_id - 1})"))

    case = Case(**data)
    db.add(case)
    await db.flush()
    await db.refresh(case)

    return CaseResponse.model_validate(case)


@router.patch("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: int,
    case_in: CaseUpdate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(require_api_key),
):
    """
    Partially update a case. Only provided fields are modified.
    Requires API key authentication.
    """
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.is_deleted == False)  # noqa: E712
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    update_data = case_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(case, field, value)

    case.version += 1
    await db.flush()
    await db.refresh(case)

    return CaseResponse.model_validate(case)


@router.delete("/{case_id}", response_model=MessageResponse)
async def delete_case(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(require_api_key),
):
    """
    Soft-delete a case. The record is marked as deleted but preserved
    for audit purposes. Requires API key authentication.
    """
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.is_deleted == False)  # noqa: E712
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    case.is_deleted = True
    await db.flush()

    return MessageResponse(message=f"Case {case_id} soft-deleted successfully")


@router.get("/{case_id}/dockets")
async def get_case_dockets(case_id: int, db: AsyncSession = Depends(get_db)):
    """Get all dockets for a specific case."""
    result = await db.execute(select(Docket).where(Docket.case_id == case_id))
    return result.scalars().all()


@router.get("/{case_id}/documents")
async def get_case_documents(case_id: int, db: AsyncSession = Depends(get_db)):
    """Get all documents for a specific case."""
    result = await db.execute(
        select(Document).where(Document.case_id == case_id).order_by(Document.document_date.desc())
    )
    return result.scalars().all()


@router.get("/{case_id}/secondary-sources")
async def get_case_secondary_sources(case_id: int, db: AsyncSession = Depends(get_db)):
    """Get all secondary sources for a specific case."""
    result = await db.execute(
        select(SecondarySource).where(SecondarySource.case_id == case_id)
    )
    return result.scalars().all()
