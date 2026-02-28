"""
AIClassification model — AI-litigation-specific taxonomy.

Stores multi-dimensional classification of cases by:
- AI technology type
- Legal theory
- Industry sector
- Case outcome

Supports both manual (curator) and automated (NLP) classification.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    String,
    Float,
    DateTime,
    ForeignKey,
    func,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AIClassification(Base):
    __tablename__ = "ai_classifications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    case_id: Mapped[int] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # ── Classification Fields ────────────────────────────────────────
    ai_technology_type: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    legal_theory: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    industry_sector: Mapped[Optional[str]] = mapped_column(String(100), index=True)

    # ── Classification Metadata ──────────────────────────────────────
    classification_source: Mapped[Optional[str]] = mapped_column(String(50))
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)
    classified_by: Mapped[Optional[str]] = mapped_column(String(100))

    # ── Review Status ────────────────────────────────────────────────
    verified_by: Mapped[Optional[str]] = mapped_column(String(100))
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # ── Timestamps ───────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # ── Relationships ────────────────────────────────────────────────
    case: Mapped["Case"] = relationship(back_populates="ai_classifications")  # type: ignore[name-defined]

    __table_args__ = (
        Index("ix_ai_class_tech_theory", "ai_technology_type", "legal_theory"),
    )

    def __repr__(self) -> str:
        return (
            f"<AIClassification(case_id={self.case_id}, "
            f"tech={self.ai_technology_type}, theory={self.legal_theory})>"
        )
