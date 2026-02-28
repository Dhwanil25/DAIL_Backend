"""
Documents API — CRUD endpoints for case documents.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import PaginationDep, require_api_key
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse[DocumentResponse])
async def list_documents(
    pagination: PaginationDep = Depends(),
    db: AsyncSession = Depends(get_db),
    case_id: Optional[int] = Query(None, description="Filter by case"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    search: Optional[str] = Query(None, description="Search document title"),
):
    """List documents with optional filtering."""
    query = select(Document)

    if case_id:
        query = query.where(Document.case_id == case_id)
    if document_type:
        query = query.where(Document.document_type == document_type)
    if search:
        query = query.where(Document.document_title.ilike(f"%{search}%"))

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    query = (
        query.order_by(Document.document_date.desc().nullslast())
        .offset(pagination.offset)
        .limit(pagination.page_size)
    )
    result = await db.execute(query)
    documents = result.scalars().all()

    return PaginatedResponse.create(
        items=[DocumentResponse.model_validate(d) for d in documents],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single document by ID."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
    return DocumentResponse.model_validate(doc)


@router.post("", response_model=DocumentResponse, status_code=201)
async def create_document(
    doc_in: DocumentCreate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(require_api_key),
):
    """Create a new document. Requires API key."""
    doc = Document(**doc_in.model_dump())
    db.add(doc)
    await db.flush()
    await db.refresh(doc)
    return DocumentResponse.model_validate(doc)


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    doc_in: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(require_api_key),
):
    """Update a document. Requires API key."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")

    for field, value in doc_in.model_dump(exclude_unset=True).items():
        setattr(doc, field, value)

    await db.flush()
    await db.refresh(doc)
    return DocumentResponse.model_validate(doc)


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(require_api_key),
):
    """Delete a document. Requires API key."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
    await db.delete(doc)
