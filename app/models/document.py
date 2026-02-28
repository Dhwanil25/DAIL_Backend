"""
Document model — case-related documents (filings, orders, briefs).

Stores metadata and links to PACER/RECAP documents.
"""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    String,
    Text,
    Integer,
    BigInteger,
    Date,
    DateTime,
    ForeignKey,
    func,
    Index,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # ── Foreign Keys ─────────────────────────────────────────────────
    case_id: Mapped[int] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    docket_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("dockets.id", ondelete="SET NULL"), index=True
    )

    # ── Document Identifiers ─────────────────────────────────────────
    document_type: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    document_title: Mapped[Optional[str]] = mapped_column(Text)
    document_date: Mapped[Optional[date]] = mapped_column(Date, index=True)

    # ── Source & Links ───────────────────────────────────────────────
    cite_or_reference: Mapped[Optional[str]] = mapped_column(Text)
    link: Mapped[Optional[str]] = mapped_column(Text)

    # ── RECAP Integration ────────────────────────────────────────────
    courtlistener_recap_id: Mapped[Optional[int]] = mapped_column(Integer)
    pacer_doc_id: Mapped[Optional[str]] = mapped_column(String(50))
    page_count: Mapped[Optional[int]] = mapped_column(Integer)

    # ── Extracted Text ───────────────────────────────────────────────
    extracted_text: Mapped[Optional[str]] = mapped_column(Text)
    search_vector: Mapped[Optional[str]] = mapped_column(TSVECTOR)

    # ── File Storage ─────────────────────────────────────────────────
    storage_url: Mapped[Optional[str]] = mapped_column(Text)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100))

    # ── Timestamps ───────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # ── Relationships ────────────────────────────────────────────────
    case: Mapped["Case"] = relationship(back_populates="documents")  # type: ignore[name-defined]

    __table_args__ = (
        Index("ix_documents_search_vector", "search_vector", postgresql_using="gin"),
    )

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, title='{(self.document_title or '')[:50]}')>"
