"""
Opinion schemas — request/response models for Opinions API.
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class OpinionBase(BaseModel):
    opinion_type: Optional[str] = "majority"
    author_str: Optional[str] = Field(None, max_length=500)
    plain_text: Optional[str] = None
    html: Optional[str] = None
    word_count: Optional[int] = None


class OpinionCreate(OpinionBase):
    cluster_id: int


class OpinionResponse(OpinionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cluster_id: int
    courtlistener_opinion_id: Optional[int] = None
    created_at: datetime


class OpinionClusterBase(BaseModel):
    case_name: Optional[str] = None
    date_filed: Optional[date] = None
    judges: Optional[str] = None
    procedural_history: Optional[str] = None
    syllabus: Optional[str] = None
    citation_count: int = 0


class OpinionClusterCreate(OpinionClusterBase):
    case_id: int
    docket_id: Optional[int] = None


class OpinionClusterResponse(OpinionClusterBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    case_id: int
    docket_id: Optional[int] = None
    courtlistener_cluster_id: Optional[int] = None
    opinions: list[OpinionResponse] = []
    created_at: datetime
    updated_at: datetime
