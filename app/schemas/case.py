"""Pydantic schemas for the Cases table."""

from __future__ import annotations

from datetime import date as DateType
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ── Brief nested schemas (avoid circular imports) ────────────────────
class DocketBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    court: Optional[str] = None
    number: Optional[str] = None
    link: Optional[str] = None


class DocumentBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    court: Optional[str] = None
    date: Optional[DateType] = None
    link: Optional[str] = None
    cite_or_reference: Optional[str] = None


class SecondarySourceBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    secondary_source_link: Optional[str] = None
    secondary_source_title: Optional[str] = None


# ── Case Base (shared fields) ───────────────────────────────────────
class CaseBase(BaseModel):
    record_number: int
    case_slug: Optional[str] = None
    caption: str
    brief_description: Optional[str] = None
    area_of_application: Optional[str] = None
    area_of_application_text: Optional[str] = None
    issue_text: Optional[str] = None
    issue_list: Optional[str] = None
    cause_of_action_list: Optional[str] = None
    cause_of_action_text: Optional[str] = None
    name_of_algorithm_list: Optional[str] = None
    name_of_algorithm_text: Optional[str] = None
    class_action_list: Optional[str] = None
    class_action: Optional[str] = None
    organizations_involved: Optional[str] = None
    jurisdiction_filed: Optional[str] = None
    date_action_filed: Optional[DateType] = None
    current_jurisdiction: Optional[str] = None
    jurisdiction_type: Optional[str] = None
    jurisdiction_type_text: Optional[str] = None
    jurisdiction_name: Optional[str] = None
    published_opinions: Optional[str] = None
    published_opinions_binary: bool = False
    status_disposition: Optional[str] = None
    progress_notes: Optional[str] = None
    researcher: Optional[str] = None
    summary_of_significance: Optional[str] = None
    summary_facts_activity: Optional[str] = None
    most_recent_activity: Optional[str] = None
    most_recent_activity_date: Optional[DateType] = None
    keyword: Optional[str] = None


class CaseCreate(CaseBase):
    """Schema for creating a new case. record_number + caption required."""
    pass


class CaseUpdate(BaseModel):
    """Schema for updating a case. All fields optional."""
    record_number: Optional[int] = None
    case_slug: Optional[str] = None
    caption: Optional[str] = None
    brief_description: Optional[str] = None
    area_of_application: Optional[str] = None
    area_of_application_text: Optional[str] = None
    issue_text: Optional[str] = None
    issue_list: Optional[str] = None
    cause_of_action_list: Optional[str] = None
    cause_of_action_text: Optional[str] = None
    name_of_algorithm_list: Optional[str] = None
    name_of_algorithm_text: Optional[str] = None
    class_action_list: Optional[str] = None
    class_action: Optional[str] = None
    organizations_involved: Optional[str] = None
    jurisdiction_filed: Optional[str] = None
    date_action_filed: Optional[DateType] = None
    current_jurisdiction: Optional[str] = None
    jurisdiction_type: Optional[str] = None
    jurisdiction_type_text: Optional[str] = None
    jurisdiction_name: Optional[str] = None
    published_opinions: Optional[str] = None
    published_opinions_binary: Optional[bool] = None
    status_disposition: Optional[str] = None
    progress_notes: Optional[str] = None
    researcher: Optional[str] = None
    summary_of_significance: Optional[str] = None
    summary_facts_activity: Optional[str] = None
    most_recent_activity: Optional[str] = None
    most_recent_activity_date: Optional[DateType] = None
    keyword: Optional[str] = None


class CaseResponse(CaseBase):
    """Full case response including auto-generated fields."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    date_added: Optional[datetime] = None
    last_update: Optional[datetime] = None


class CaseDetailResponse(CaseResponse):
    """Case with nested dockets, documents, and secondary sources."""
    dockets: list[DocketBrief] = []
    documents: list[DocumentBrief] = []
    secondary_sources: list[SecondarySourceBrief] = []
