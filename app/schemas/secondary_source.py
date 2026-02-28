"""
SecondarySource schemas — request/response models.
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class SecondarySourceBase(BaseModel):
    title: Optional[str] = None
    link: Optional[str] = None
    source_name: Optional[str] = Field(None, max_length=500)
    author: Optional[str] = Field(None, max_length=500)
    publication_date: Optional[date] = None
    source_type: Optional[str] = Field(None, max_length=100)


class SecondarySourceCreate(SecondarySourceBase):
    case_id: int


class SecondarySourceUpdate(SecondarySourceBase):
    pass


class SecondarySourceResponse(SecondarySourceBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    case_id: int
    created_at: datetime
    updated_at: datetime
