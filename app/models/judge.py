"""
Judge model — biographical data for judges assigned to AI litigation cases.

Linked to Free Law Project's judge database via courtlistener_person_id.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    String,
    Integer,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Judge(Base):
    __tablename__ = "judges"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # ── Identity ─────────────────────────────────────────────────────
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    name_normalized: Mapped[Optional[str]] = mapped_column(String(500), index=True)

    # ── CourtListener Integration ────────────────────────────────────
    courtlistener_person_id: Mapped[Optional[int]] = mapped_column(
        Integer, unique=True, index=True
    )

    # ── Position Info ────────────────────────────────────────────────
    position_title: Mapped[Optional[str]] = mapped_column(String(255))
    court_name: Mapped[Optional[str]] = mapped_column(String(500))
    appointed_by: Mapped[Optional[str]] = mapped_column(String(500))

    # ── Entity Resolution ────────────────────────────────────────────
    canonical_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("judges.id", ondelete="SET NULL")
    )
    is_alias: Mapped[bool] = mapped_column(server_default="false")

    # ── Timestamps ───────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # ── Relationships ────────────────────────────────────────────────
    case_judges: Mapped[list["CaseJudge"]] = relationship(
        back_populates="judge", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Judge(id={self.id}, name='{self.name}')>"


class CaseJudge(Base):
    """Junction table: assigns judges to cases with role context."""
    __tablename__ = "case_judges"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    case_id: Mapped[int] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    judge_id: Mapped[int] = mapped_column(
        ForeignKey("judges.id", ondelete="CASCADE"), nullable=False, index=True
    )

    role: Mapped[Optional[str]] = mapped_column(String(50))

    # ── Relationships ────────────────────────────────────────────────
    case: Mapped["Case"] = relationship(back_populates="case_judges")  # type: ignore[name-defined]
    judge: Mapped["Judge"] = relationship(back_populates="case_judges")

    def __repr__(self) -> str:
        return f"<CaseJudge(case_id={self.case_id}, judge_id={self.judge_id})>"
