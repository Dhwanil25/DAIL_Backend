"""
Party schemas — request/response models for Parties API.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class PartyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=1000)
    party_type: Optional[str] = "other"


class PartyCreate(PartyBase):
    pass


class PartyUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=1000)
    party_type: Optional[str] = None


class PartyResponse(PartyBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name_normalized: Optional[str] = None
    canonical_id: Optional[int] = None
    is_alias: bool = False
    created_at: datetime
    updated_at: datetime


class CasePartyCreate(BaseModel):
    case_id: int
    party_id: int
    role: str = "other"
    attorney_name: Optional[str] = Field(None, max_length=500)
    attorney_firm: Optional[str] = Field(None, max_length=500)


class CasePartyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    case_id: int
    party_id: int
    role: Optional[str] = None
    attorney_name: Optional[str] = None
    attorney_firm: Optional[str] = None
    party: Optional[PartyResponse] = None
