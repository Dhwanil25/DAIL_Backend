"""
SQLAlchemy ORM model for the Dockets table.
Maps 1:1 to Caspio Docket_Table.
FK: case_number -> cases.record_number
"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.case import Case


class Docket(Base):
    __tablename__ = "dockets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_number: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cases.record_number", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    court: Mapped[Optional[str]] = mapped_column(Text)
    number: Mapped[Optional[str]] = mapped_column(Text)
    link: Mapped[Optional[str]] = mapped_column(Text)

    # ── Relationship ─────────────────────────────────────────────────
    case: Mapped["Case"] = relationship(back_populates="dockets")

    def __repr__(self) -> str:
        return f"<Docket(id={self.id}, case_number={self.case_number}, number='{self.number}')>"
