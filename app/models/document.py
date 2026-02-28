"""
SQLAlchemy ORM model for the Documents table.
Maps 1:1 to Caspio Document_Table.
FK: case_number -> cases.record_number
"""

from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.case import Case


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_number: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cases.record_number", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    court: Mapped[Optional[str]] = mapped_column(Text)
    date: Mapped[Optional[date]] = mapped_column(Date)
    link: Mapped[Optional[str]] = mapped_column(Text)
    cite_or_reference: Mapped[Optional[str]] = mapped_column(Text)

    # ── Relationship ─────────────────────────────────────────────────
    case: Mapped["Case"] = relationship(back_populates="documents")

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, case_number={self.case_number})>"
