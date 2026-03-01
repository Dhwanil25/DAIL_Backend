"""Pydantic schemas for the Documents table."""

from __future__ import annotations

from datetime import date as DateType
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DocumentBase(BaseModel):
    case_number: int
    court: Optional[str] = None
    date: Optional[DateType] = None
    link: Optional[str] = None
    cite_or_reference: Optional[str] = None
    document: Optional[str] = None


class DocumentCreate(DocumentBase):
    """Create a document. case_number required."""
    pass


class DocumentUpdate(BaseModel):
    """Update a document. All fields optional."""
    case_number: Optional[int] = None
    court: Optional[str] = None
    date: Optional[DateType] = None
    link: Optional[str] = None
    cite_or_reference: Optional[str] = None
    document: Optional[str] = None


class DocumentResponse(DocumentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
