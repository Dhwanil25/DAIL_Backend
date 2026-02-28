"""
Case schemas — request/response models for the Cases API.

Field names match the database migration (002_align_gwu_form_fields).
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
    summary_of_facts: Optional[str] = Field(None, description="Summary of Facts and Activity to Date")
    area_of_application: Optional[str] = Field(None, max_length=255)
    area_of_application_list: Optional[str] = Field(None, max_length=255, description="Standardised area dropdown")
    algorithm_name: Optional[str] = Field(None, max_length=500)
    algorithm_list: Optional[str] = Field(None, max_length=500, description="Standardised algorithm dropdown")
    algorithm_description: Optional[str] = None
    issue_text: Optional[str] = None
    issue_list: Optional[str] = Field(None, max_length=255, description="Standardised issue dropdown")
    cause_of_action: Optional[str] = None
    class_action: Optional[str] = Field(None, max_length=50, description="Class action status: Yes/No/Putative")
    jurisdiction_name: Optional[str] = Field(None, max_length=255)
    jurisdiction_type: Optional[str] = Field(None, max_length=100)
    jurisdiction_state: Optional[str] = Field(None, max_length=100)
    jurisdiction_municipality: Optional[str] = Field(None, max_length=255)
    jurisdiction_filed: Optional[str] = Field(None, max_length=255, description="Original filing jurisdiction")
    current_jurisdiction: Optional[str] = Field(None, max_length=255, description="Current jurisdiction")
    status_disposition: Optional[str] = Field(None, max_length=100)
    filed_date: Optional[date] = None
    closed_date: Optional[date] = None
    organizations_involved: Optional[str] = None
    keywords: Optional[str] = None
    lead_case: Optional[str] = Field(None, max_length=50)
    related_cases: Optional[str] = None
    progress_notes: Optional[str] = None
    researcher: Optional[str] = Field(None, max_length=255, description="Researcher tracking this case")
    last_updated_by: Optional[str] = Field(None, max_length=100)
    published_opinions: bool = False
    summary_of_significance: Optional[str] = None
    most_recent_activity: Optional[str] = None
    most_recent_activity_date: Optional[date] = None
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
    summary_of_facts: Optional[str] = None
    area_of_application: Optional[str] = None
    area_of_application_list: Optional[str] = None
    algorithm_name: Optional[str] = None
    algorithm_list: Optional[str] = None
    algorithm_description: Optional[str] = None
    issue_text: Optional[str] = None
    issue_list: Optional[str] = None
    cause_of_action: Optional[str] = None
    class_action: Optional[str] = None
    jurisdiction_name: Optional[str] = None
    jurisdiction_type: Optional[str] = None
    jurisdiction_state: Optional[str] = None
    jurisdiction_municipality: Optional[str] = None
    jurisdiction_filed: Optional[str] = None
    current_jurisdiction: Optional[str] = None
    status_disposition: Optional[str] = None
    filed_date: Optional[date] = None
    closed_date: Optional[date] = None
    organizations_involved: Optional[str] = None
    keywords: Optional[str] = None
    lead_case: Optional[str] = None
    related_cases: Optional[str] = None
    progress_notes: Optional[str] = None
    researcher: Optional[str] = None
    last_updated_by: Optional[str] = None
    published_opinions: Optional[bool] = None
    summary_of_significance: Optional[str] = None
    most_recent_activity: Optional[str] = None
    most_recent_activity_date: Optional[date] = None
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
    class_action: Optional[str] = None
    created_at: datetime
    updated_at: datetime
