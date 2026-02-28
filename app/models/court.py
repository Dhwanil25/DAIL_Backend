"""
Court model — represents a court where AI litigation may be filed.

Normalized against CourtListener's court database.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    String,
    DateTime,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Court(Base):
    __tablename__ = "courts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Identifiers
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    short_name: Mapped[Optional[str]] = mapped_column(String(100))
    citation_string: Mapped[Optional[str]] = mapped_column(String(100))
    courtlistener_id: Mapped[Optional[str]] = mapped_column(
        String(50), unique=True, index=True
    )
    pacer_id: Mapped[Optional[str]] = mapped_column(String(10))

    # Classification
    jurisdiction_type: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    court_level: Mapped[Optional[str]] = mapped_column(String(50))

    # Location
    state: Mapped[Optional[str]] = mapped_column(String(2))
    country: Mapped[str] = mapped_column(String(100), server_default="US")

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    dockets: Mapped[list["Docket"]] = relationship(back_populates="court", lazy="selectin")  # type: ignore[name-defined]

    def __repr__(self) -> str:
        return f"<Court(id={self.id}, name='{self.short_name or self.name}')>"
