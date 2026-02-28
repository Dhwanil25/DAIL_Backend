"""
Court schemas — request/response models for the Courts API.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class CourtBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    short_name: Optional[str] = Field(None, max_length=100)
    citation_string: Optional[str] = Field(None, max_length=100)
    courtlistener_id: Optional[str] = Field(None, max_length=50)
    pacer_id: Optional[str] = Field(None, max_length=10)
    jurisdiction_type: Optional[str] = Field(None, description="federal, state, local, etc.")
    court_level: Optional[str] = None
    state: Optional[str] = Field(None, max_length=2)
    country: str = Field("US", max_length=100)


class CourtCreate(CourtBase):
    pass


class CourtUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=500)
    short_name: Optional[str] = None
    citation_string: Optional[str] = None
    courtlistener_id: Optional[str] = None
    jurisdiction_type: Optional[str] = None
    court_level: Optional[str] = None
    state: Optional[str] = None


class CourtResponse(CourtBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
