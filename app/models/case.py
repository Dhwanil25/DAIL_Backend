"""
Case model — the central entity in DAIL.

Represents a single AI-related litigation case tracked from complaint forward.
Preserves all original Caspio fields while adding enriched metadata.

Column names match the 002_align_gwu_form_fields Alembic migration.
"""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    String,
    Text,
    Integer,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    func,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # ── DAIL Legacy Identifier (string to match Caspio "TEST-001" style) ──
    record_number: Mapped[Optional[str]] = mapped_column(
        String(50), unique=True, index=True, doc="Original DAIL/Caspio record number"
    )

    # ── Core Case Information ────────────────────────────────────────
    caption: Mapped[str] = mapped_column(
        Text, nullable=False, doc="Full case caption, e.g. 'Doe v. OpenAI'"
    )
    case_slug: Mapped[Optional[str]] = mapped_column(String(255))
    brief_description: Mapped[Optional[str]] = mapped_column(Text)
    summary_of_facts: Mapped[Optional[str]] = mapped_column(Text, doc="Summary of Facts and Activity to Date")

    # ── AI-Specific Classification ───────────────────────────────────
    area_of_application: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    area_of_application_list: Mapped[Optional[str]] = mapped_column(String(255), doc="Standardised area dropdown value")
    issue_text: Mapped[Optional[str]] = mapped_column(Text)
    issue_list: Mapped[Optional[str]] = mapped_column(String(255), doc="Standardised issue dropdown value")
    cause_of_action: Mapped[Optional[str]] = mapped_column(Text)
    algorithm_name: Mapped[Optional[str]] = mapped_column(String(500))
    algorithm_list: Mapped[Optional[str]] = mapped_column(String(500), doc="Standardised algorithm dropdown value")
    algorithm_description: Mapped[Optional[str]] = mapped_column(Text)

    # ── Jurisdiction & Filing ────────────────────────────────────────
    class_action: Mapped[Optional[str]] = mapped_column(String(50), doc="Class action status: Yes/No/Putative")
    jurisdiction_name: Mapped[Optional[str]] = mapped_column(String(255))
    jurisdiction_type: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    jurisdiction_state: Mapped[Optional[str]] = mapped_column(String(100))
    jurisdiction_municipality: Mapped[Optional[str]] = mapped_column(String(255))
    jurisdiction_filed: Mapped[Optional[str]] = mapped_column(String(255), doc="Original filing jurisdiction")
    current_jurisdiction: Mapped[Optional[str]] = mapped_column(String(255), doc="Where case currently resides")

    # ── Status & Dates ───────────────────────────────────────────────
    status_disposition: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    filed_date: Mapped[Optional[date]] = mapped_column(Date, index=True)
    closed_date: Mapped[Optional[date]] = mapped_column(Date)

    # ── Metadata ─────────────────────────────────────────────────────
    organizations_involved: Mapped[Optional[str]] = mapped_column(Text)
    keywords: Mapped[Optional[str]] = mapped_column(Text)
    lead_case: Mapped[Optional[str]] = mapped_column(String(50))
    related_cases: Mapped[Optional[str]] = mapped_column(Text)
    progress_notes: Mapped[Optional[str]] = mapped_column(Text, doc="Progress notes")
    researcher: Mapped[Optional[str]] = mapped_column(String(255), doc="Researcher tracking this case")
    last_updated_by: Mapped[Optional[str]] = mapped_column(String(100))
    published_opinions: Mapped[bool] = mapped_column(Boolean, default=False, doc="Has published opinions?")
    summary_of_significance: Mapped[Optional[str]] = mapped_column(Text, doc="Summary of case significance")
    most_recent_activity: Mapped[Optional[str]] = mapped_column(Text, doc="Description of most recent activity")
    most_recent_activity_date: Mapped[Optional[date]] = mapped_column(Date, doc="Date of most recent activity")

    # ── Enriched Classification (JSONB) ──────────────────────────────
    ai_technology_types: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)
    legal_theories: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)
    industry_sectors: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)

    # ── Full-Text Search Vector ──────────────────────────────────────
    search_vector: Mapped[Optional[str]] = mapped_column(TSVECTOR)

    # ── Soft Delete & Versioning ─────────────────────────────────────
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    superseded_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("cases.id"), nullable=True
    )

    # ── Timestamps ───────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # ── Relationships ────────────────────────────────────────────────
    dockets: Mapped[list["Docket"]] = relationship(  # type: ignore[name-defined]
        back_populates="case", lazy="selectin", cascade="all, delete-orphan"
    )
    documents: Mapped[list["Document"]] = relationship(  # type: ignore[name-defined]
        back_populates="case", lazy="selectin", cascade="all, delete-orphan"
    )
    secondary_sources: Mapped[list["SecondarySource"]] = relationship(  # type: ignore[name-defined]
        back_populates="case", lazy="selectin", cascade="all, delete-orphan"
    )
    opinion_clusters: Mapped[list["OpinionCluster"]] = relationship(  # type: ignore[name-defined]
        back_populates="case", lazy="selectin", cascade="all, delete-orphan"
    )
    case_parties: Mapped[list["CaseParty"]] = relationship(  # type: ignore[name-defined]
        back_populates="case", lazy="selectin", cascade="all, delete-orphan"
    )
    case_judges: Mapped[list["CaseJudge"]] = relationship(  # type: ignore[name-defined]
        back_populates="case", lazy="selectin", cascade="all, delete-orphan"
    )
    ai_classifications: Mapped[list["AIClassification"]] = relationship(  # type: ignore[name-defined]
        back_populates="case", lazy="selectin", cascade="all, delete-orphan"
    )
    provenance_records: Mapped[list["Provenance"]] = relationship(  # type: ignore[name-defined]
        back_populates="case", lazy="selectin", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_cases_search_vector", "search_vector", postgresql_using="gin"),
        Index("ix_cases_ai_tech_types", "ai_technology_types", postgresql_using="gin"),
        Index("ix_cases_legal_theories", "legal_theories", postgresql_using="gin"),
    )

    def __repr__(self) -> str:
        return f"<Case(id={self.id}, caption='{self.caption[:50]}')>"
