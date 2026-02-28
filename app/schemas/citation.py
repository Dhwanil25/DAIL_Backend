"""
Citation schemas — request/response models for Citations API.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class CitationBase(BaseModel):
    citation_text: str = Field(..., min_length=1, description="Original citation text")
    citation_type: Optional[str] = "full_case"
    volume: Optional[str] = None
    reporter: Optional[str] = Field(None, max_length=100)
    page: Optional[str] = None
    pin_cite: Optional[str] = Field(None, max_length=50)
    year: Optional[int] = None
    court_cite: Optional[str] = Field(None, max_length=100)
    plaintiff_name: Optional[str] = Field(None, max_length=500)
    defendant_name: Optional[str] = Field(None, max_length=500)
    depth: int = 1


class CitationCreate(CitationBase):
    citing_case_id: Optional[int] = None
    cited_case_id: Optional[int] = None
    citing_opinion_id: Optional[int] = None
    cited_opinion_id: Optional[int] = None


class CitationResponse(CitationBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    citing_case_id: Optional[int] = None
    cited_case_id: Optional[int] = None
    citing_opinion_id: Optional[int] = None
    courtlistener_verified: bool = False
    created_at: datetime
