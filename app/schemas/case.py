"""
Case schemas — request/response models for the Cases API.

Field names match the database migration (001_initial_schema) exactly.
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# ── Nested response schemas ──────────────────────────────────────────────
class DocketBrief(BaseModel):
    """Minimal docket info embedded in case responses."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    docket_number: Optional[str] = None
    court_name: Optional[str] = None
    courtlistener_url: Optional[str] = None


class DocumentBrief(BaseModel):
    """Minimal document info embedded in case responses."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    document_title: Optional[str] = None
    document_type: Optional[str] = None
    document_date: Optional[date] = None
    link: Optional[str] = None


class SecondarySourceBrief(BaseModel):
    """Minimal secondary source info."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: Optional[str] = None
    link: Optional[str] = None
    source_name: Optional[str] = None


class AIClassificationBrief(BaseModel):
    """Classification info embedded in case responses."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    ai_technology_type: Optional[str] = None
    legal_theory: Optional[str] = None
    industry_sector: Optional[str] = None
    confidence_score: Optional[float] = None


class CasePartyBrief(BaseModel):
    """Party info embedded in case responses."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    role: Optional[str] = None
    attorney_name: Optional[str] = None


# ── Case Base ────────────────────────────────────────────────────────────
class CaseBase(BaseModel):
    """Shared fields for case creation and update."""
    caption: str = Field(..., min_length=1, description="Full case caption")
    case_slug: Optional[str] = Field(None, max_length=255)
    brief_description: Optional[str] = None
    facts: Optional[str] = None
    area_of_application: Optional[str] = Field(None, max_length=255)
    algorithm_name: Optional[str] = Field(None, max_length=500)
    algorithm_description: Optional[str] = None
    issue_text: Optional[str] = None
    cause_of_action: Optional[str] = None
    is_class_action: bool = False
    jurisdiction_name: Optional[str] = Field(None, max_length=255)
    jurisdiction_type: Optional[str] = Field(None, max_length=100)
    jurisdiction_state: Optional[str] = Field(None, max_length=100)
    jurisdiction_municipality: Optional[str] = Field(None, max_length=255)
    status_disposition: Optional[str] = Field(None, max_length=100)
    filed_date: Optional[date] = None
    closed_date: Optional[date] = None
    organizations_involved: Optional[str] = None
    keywords: Optional[str] = None
    lead_case: Optional[str] = Field(None, max_length=50)
    related_cases: Optional[str] = None
    notes: Optional[str] = None
    last_updated_by: Optional[str] = Field(None, max_length=100)
    ai_technology_types: Optional[list[str]] = None
    legal_theories: Optional[list[str]] = None
    industry_sectors: Optional[list[str]] = None


class CaseCreate(CaseBase):
    """Schema for creating a new case."""
    record_number: Optional[str] = Field(None, max_length=50, description="Legacy DAIL/Caspio record number")


class CaseUpdate(BaseModel):
    """Schema for updating a case (all fields optional)."""
    caption: Optional[str] = Field(None, min_length=1)
    case_slug: Optional[str] = None
    brief_description: Optional[str] = None
    facts: Optional[str] = None
    area_of_application: Optional[str] = None
    algorithm_name: Optional[str] = None
    algorithm_description: Optional[str] = None
    issue_text: Optional[str] = None
    cause_of_action: Optional[str] = None
    is_class_action: Optional[bool] = None
    jurisdiction_name: Optional[str] = None
    jurisdiction_type: Optional[str] = None
    jurisdiction_state: Optional[str] = None
    jurisdiction_municipality: Optional[str] = None
    status_disposition: Optional[str] = None
    filed_date: Optional[date] = None
    closed_date: Optional[date] = None
    organizations_involved: Optional[str] = None
    keywords: Optional[str] = None
    lead_case: Optional[str] = None
    related_cases: Optional[str] = None
    notes: Optional[str] = None
    last_updated_by: Optional[str] = None
    ai_technology_types: Optional[list[str]] = None
    legal_theories: Optional[list[str]] = None
    industry_sectors: Optional[list[str]] = None


class CaseResponse(CaseBase):
    """Full case response with all relationships."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    record_number: Optional[str] = None
    version: int = 1
    is_deleted: bool = False
    created_at: datetime
    updated_at: datetime

    # Related entities
    dockets: list[DocketBrief] = []
    documents: list[DocumentBrief] = []
    secondary_sources: list[SecondarySourceBrief] = []
    ai_classifications: list[AIClassificationBrief] = []


class CaseListResponse(BaseModel):
    """Compact case listing for search results."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    record_number: Optional[str] = None
    caption: str
    area_of_application: Optional[str] = None
    jurisdiction_name: Optional[str] = None
    jurisdiction_type: Optional[str] = None
    filed_date: Optional[date] = None
    status_disposition: Optional[str] = None
    is_class_action: bool = False
    created_at: datetime
    updated_at: datetime
