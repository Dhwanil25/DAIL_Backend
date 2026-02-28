"""
SQLAlchemy ORM model for the Secondary Sources table.
Maps 1:1 to Caspio Secondary_Source_Coverage.
FK: case_number -> cases.record_number
"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.case import Case


class SecondarySource(Base):
    __tablename__ = "secondary_sources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_number: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cases.record_number", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    secondary_source_link: Mapped[Optional[str]] = mapped_column(Text)
    secondary_source_title: Mapped[Optional[str]] = mapped_column(Text)

    # ── Relationship ─────────────────────────────────────────────────
    case: Mapped["Case"] = relationship(back_populates="secondary_sources")

    def __repr__(self) -> str:
        return f"<SecondarySource(id={self.id}, case_number={self.case_number})>"
