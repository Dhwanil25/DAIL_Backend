"""
Document schemas — request/response models for Documents API.
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class DocumentBase(BaseModel):
    document_title: Optional[str] = None
    document_type: Optional[str] = "other"
    link: Optional[str] = None
    cite_or_reference: Optional[str] = None
    document_date: Optional[date] = None
    page_count: Optional[int] = None
    mime_type: Optional[str] = Field(None, max_length=100)


class DocumentCreate(DocumentBase):
    case_id: int
    docket_id: Optional[int] = None


class DocumentUpdate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    case_id: int
    docket_id: Optional[int] = None
    courtlistener_recap_id: Optional[int] = None
    pacer_doc_id: Optional[str] = None
    storage_url: Optional[str] = None
    file_size_bytes: Optional[int] = None
    created_at: datetime
    updated_at: datetime
