"""
Provenance model — data lineage and source tracking.

Every record in the database should have provenance entries
documenting where the data came from and how it was processed.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    String,
    Text,
    Float,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Provenance(Base):
    """Tracks the origin and processing history of every data record."""
    __tablename__ = "provenance"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # ── What Record ──────────────────────────────────────────────────
    case_id: Mapped[int] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # ── Source Information ───────────────────────────────────────────
    source_system: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    source_identifier: Mapped[Optional[str]] = mapped_column(String(255))

    # ── Ingestion Details ────────────────────────────────────────────
    ingestion_method: Mapped[Optional[str]] = mapped_column(String(50))
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # ── Processing Details ───────────────────────────────────────────
    processing_steps: Mapped[Optional[dict]] = mapped_column(JSONB)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)

    # ── Notes ────────────────────────────────────────────────────────
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # ── Relationships ────────────────────────────────────────────────
    case: Mapped["Case"] = relationship(back_populates="provenance_records")  # type: ignore[name-defined]

    def __repr__(self) -> str:
        return (
            f"<Provenance(id={self.id}, case_id={self.case_id}, "
            f"source='{self.source_system}')>"
        )
