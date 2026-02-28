"""
Docket schemas — request/response models for the Dockets API.
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class DocketBase(BaseModel):
    docket_number: Optional[str] = Field(None, max_length=100)
    court_name: Optional[str] = Field(None, max_length=500)
    courtlistener_docket_id: Optional[int] = None
    courtlistener_url: Optional[str] = None
    pacer_case_id: Optional[str] = Field(None, max_length=50)
    date_filed: Optional[date] = None
    date_terminated: Optional[date] = None
    nature_of_suit: Optional[str] = Field(None, max_length=500)
    plaintiff_summary: Optional[str] = None
    defendant_summary: Optional[str] = None
    link: Optional[str] = None


class DocketCreate(DocketBase):
    case_id: int
    court_id: Optional[int] = None


class DocketUpdate(DocketBase):
    pass


class DocketResponse(DocketBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    case_id: int
    court_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
