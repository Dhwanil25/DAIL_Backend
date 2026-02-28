"""
SQLAlchemy ORM model for the Cases table.
Maps 1:1 to Caspio Case_Table (minus deprecated *_OLD fields).
"""

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, DateTime, Integer, Text, func
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.docket import Docket
    from app.models.document import Document
    from app.models.secondary_source import SecondarySource


class Case(Base):
    __tablename__ = "cases"

    # ── Primary / Business Keys ──────────────────────────────────────
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    record_number: Mapped[int] = mapped_column(
        Integer, unique=True, nullable=False, index=True,
    )
    case_slug: Mapped[Optional[str]] = mapped_column(Text)
    caption: Mapped[str] = mapped_column(Text, nullable=False)
    brief_description: Mapped[Optional[str]] = mapped_column(Text)

    # ── Area of Application ──────────────────────────────────────────
    area_of_application: Mapped[Optional[str]] = mapped_column(Text, index=True)
    area_of_application_text: Mapped[Optional[str]] = mapped_column(Text)

    # ── Issues ───────────────────────────────────────────────────────
    issue_text: Mapped[Optional[str]] = mapped_column(Text)
    issue_list: Mapped[Optional[str]] = mapped_column(Text)

    # ── Cause of Action ──────────────────────────────────────────────
    cause_of_action_list: Mapped[Optional[str]] = mapped_column(Text)
    cause_of_action_text: Mapped[Optional[str]] = mapped_column(Text)

    # ── Algorithm ────────────────────────────────────────────────────
    name_of_algorithm_list: Mapped[Optional[str]] = mapped_column(Text)
    name_of_algorithm_text: Mapped[Optional[str]] = mapped_column(Text)

    # ── Class Action ─────────────────────────────────────────────────
    class_action_list: Mapped[Optional[str]] = mapped_column(Text)
    class_action: Mapped[Optional[str]] = mapped_column(Text)

    # ── Organizations ────────────────────────────────────────────────
    organizations_involved: Mapped[Optional[str]] = mapped_column(Text)

    # ── Jurisdiction ─────────────────────────────────────────────────
    jurisdiction_filed: Mapped[Optional[str]] = mapped_column(Text)
    date_action_filed: Mapped[Optional[date]] = mapped_column(Date, index=True)
    current_jurisdiction: Mapped[Optional[str]] = mapped_column(Text)
    jurisdiction_type: Mapped[Optional[str]] = mapped_column(Text, index=True)
    jurisdiction_type_text: Mapped[Optional[str]] = mapped_column(Text)
    jurisdiction_name: Mapped[Optional[str]] = mapped_column(Text)

    # ── Published Opinions ───────────────────────────────────────────
    published_opinions: Mapped[Optional[str]] = mapped_column(Text)
    published_opinions_binary: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false",
    )

    # ── Status / Disposition ─────────────────────────────────────────
    status_disposition: Mapped[Optional[str]] = mapped_column(Text, index=True)

    # ── Timestamps ───────────────────────────────────────────────────
    date_added: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )
    last_update: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(),
    )

    # ── Notes & Research ─────────────────────────────────────────────
    progress_notes: Mapped[Optional[str]] = mapped_column(Text)
    researcher: Mapped[Optional[str]] = mapped_column(Text)

    # ── Summaries ────────────────────────────────────────────────────
    summary_of_significance: Mapped[Optional[str]] = mapped_column(Text)
    summary_facts_activity: Mapped[Optional[str]] = mapped_column(Text)

    # ── Recent Activity ──────────────────────────────────────────────
    most_recent_activity: Mapped[Optional[str]] = mapped_column(Text)
    most_recent_activity_date: Mapped[Optional[date]] = mapped_column(Date)

    # ── Search ───────────────────────────────────────────────────────
    keyword: Mapped[Optional[str]] = mapped_column(Text)
    search_vector = mapped_column(TSVECTOR)

    # ── Relationships ────────────────────────────────────────────────
    dockets: Mapped[list["Docket"]] = relationship(
        back_populates="case",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    documents: Mapped[list["Document"]] = relationship(
        back_populates="case",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    secondary_sources: Mapped[list["SecondarySource"]] = relationship(
        back_populates="case",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Case(id={self.id}, record_number={self.record_number}, caption='{self.caption[:50] if self.caption else ''}')>"
