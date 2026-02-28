"""
Party models — entities involved in litigation.

Uses a junction table (CaseParty) to handle many-to-many relationships
between parties and cases, with role classification.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Party(Base):
    """A legal entity (person, company, government body) that participates in cases."""
    __tablename__ = "parties"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # ── Identity ─────────────────────────────────────────────────────
    name: Mapped[str] = mapped_column(String(1000), nullable=False, index=True)
    name_normalized: Mapped[Optional[str]] = mapped_column(String(1000), index=True)
    party_type: Mapped[Optional[str]] = mapped_column(String(50))

    # ── Entity Resolution ────────────────────────────────────────────
    canonical_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("parties.id", ondelete="SET NULL")
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
    case_parties: Mapped[list["CaseParty"]] = relationship(
        back_populates="party", lazy="selectin"
    )
    aliases: Mapped[list["Party"]] = relationship(
        foreign_keys=[canonical_id], lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Party(id={self.id}, name='{self.name}')>"


class CaseParty(Base):
    """Junction table: many-to-many between Case and Party, with role context."""
    __tablename__ = "case_parties"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    case_id: Mapped[int] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    party_id: Mapped[int] = mapped_column(
        ForeignKey("parties.id", ondelete="CASCADE"), nullable=False, index=True
    )

    role: Mapped[Optional[str]] = mapped_column(String(50))
    attorney_name: Mapped[Optional[str]] = mapped_column(String(500))
    attorney_firm: Mapped[Optional[str]] = mapped_column(String(500))

    # ── Relationships ────────────────────────────────────────────────
    case: Mapped["Case"] = relationship(back_populates="case_parties")  # type: ignore[name-defined]
    party: Mapped["Party"] = relationship(back_populates="case_parties")

    def __repr__(self) -> str:
        return f"<CaseParty(case_id={self.case_id}, party_id={self.party_id}, role='{self.role}')>"
