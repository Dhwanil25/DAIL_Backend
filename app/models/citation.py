"""
Citation model — inter-case citation links with structured parsing.

Stores both raw citation text and parsed/structured components.
Designed for integration with the eyecite library.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    String,
    Text,
    Integer,
    DateTime,
    ForeignKey,
    func,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Citation(Base):
    """
    A citation extracted from opinions or documents.
    Can link two cases, or store an unresolved citation string.
    """
    __tablename__ = "citations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # ── Source & Target ──────────────────────────────────────────────
    citing_case_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"), index=True
    )
    cited_case_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("cases.id", ondelete="SET NULL"), index=True
    )
    citing_opinion_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("opinions.id", ondelete="SET NULL"), index=True
    )
    cited_opinion_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("opinions.id", ondelete="SET NULL"), index=True
    )

    # ── Citation Type ────────────────────────────────────────────────
    citation_type: Mapped[Optional[str]] = mapped_column(String(50))

    # ── Raw Data ─────────────────────────────────────────────────────
    citation_text: Mapped[str] = mapped_column(Text, nullable=False)

    # ── Parsed Components (eyecite structured output) ────────────────
    volume: Mapped[Optional[str]] = mapped_column(String(20))
    reporter: Mapped[Optional[str]] = mapped_column(String(100))
    page: Mapped[Optional[str]] = mapped_column(String(20))
    pin_cite: Mapped[Optional[str]] = mapped_column(String(50))
    year: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    court_cite: Mapped[Optional[str]] = mapped_column(String(100))
    plaintiff_name: Mapped[Optional[str]] = mapped_column(String(500))
    defendant_name: Mapped[Optional[str]] = mapped_column(String(500))

    # ── Citation Depth ───────────────────────────────────────────────
    depth: Mapped[int] = mapped_column(Integer, server_default="1")

    # ── Verification ─────────────────────────────────────────────────
    courtlistener_verified: Mapped[bool] = mapped_column(
        server_default="false"
    )

    # ── Timestamps ───────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # ── Relationships ────────────────────────────────────────────────
    citing_case: Mapped[Optional["Case"]] = relationship(  # type: ignore[name-defined]
        foreign_keys=[citing_case_id]
    )
    cited_case: Mapped[Optional["Case"]] = relationship(  # type: ignore[name-defined]
        foreign_keys=[cited_case_id]
    )

    __table_args__ = (
        Index("ix_citations_reporter_volume_page", "reporter", "volume", "page"),
    )

    def __repr__(self) -> str:
        return f"<Citation(id={self.id}, text='{self.citation_text[:60]}')>"
