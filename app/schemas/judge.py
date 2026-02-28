"""
Judge schemas — request/response models for Judges API.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class JudgeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    court_name: Optional[str] = Field(None, max_length=500)
    position_title: Optional[str] = Field(None, max_length=255)
    appointed_by: Optional[str] = Field(None, max_length=500)


class JudgeCreate(JudgeBase):
    courtlistener_person_id: Optional[int] = None


class JudgeUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=500)
    court_name: Optional[str] = None
    position_title: Optional[str] = None
    appointed_by: Optional[str] = None


class JudgeResponse(JudgeBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name_normalized: Optional[str] = None
    courtlistener_person_id: Optional[int] = None
    canonical_id: Optional[int] = None
    is_alias: bool = False
    created_at: datetime
    updated_at: datetime
