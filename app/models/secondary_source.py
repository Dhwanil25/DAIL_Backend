"""
SecondarySource model — articles, press coverage, and scholarly work about cases.

Preserves the original Caspio SecondarySources table structure.
"""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    String,
    Text,
    Date,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SecondarySource(Base):
    __tablename__ = "secondary_sources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # ── Foreign Keys ─────────────────────────────────────────────────
    case_id: Mapped[int] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # ── Source Information ───────────────────────────────────────────
    title: Mapped[Optional[str]] = mapped_column(Text)
    link: Mapped[Optional[str]] = mapped_column(Text)
    source_name: Mapped[Optional[str]] = mapped_column(String(500))
    author: Mapped[Optional[str]] = mapped_column(String(500))
    publication_date: Mapped[Optional[date]] = mapped_column(Date)
    source_type: Mapped[Optional[str]] = mapped_column(String(100))

    # ── Timestamps ───────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # ── Relationships ────────────────────────────────────────────────
    case: Mapped["Case"] = relationship(back_populates="secondary_sources")  # type: ignore[name-defined]

    def __repr__(self) -> str:
        return f"<SecondarySource(id={self.id}, title='{(self.title or '')[:50]}')>"
