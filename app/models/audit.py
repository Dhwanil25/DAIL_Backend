"""
AuditLog model — tamper-proof audit trail for all data changes.

Uses PostgreSQL triggers (created in migration) to automatically
capture every INSERT, UPDATE, DELETE across tracked tables.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    String,
    Integer,
    DateTime,
    func,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AuditLog(Base):
    """Immutable audit log record. One row per data change."""
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # ── What Changed ─────────────────────────────────────────────────
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    table_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    record_id: Mapped[Optional[int]] = mapped_column(Integer, index=True)

    # ── Change Data ──────────────────────────────────────────────────
    old_values: Mapped[Optional[dict]] = mapped_column(JSONB)
    new_values: Mapped[Optional[dict]] = mapped_column(JSONB)
    changed_fields: Mapped[Optional[dict]] = mapped_column(JSONB)

    # ── Who Changed It ───────────────────────────────────────────────
    changed_by: Mapped[Optional[str]] = mapped_column(String(100))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))

    # ── Request Context ──────────────────────────────────────────────
    request_id: Mapped[Optional[str]] = mapped_column(String(50))

    # ── Timestamp (immutable) ────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_audit_log_table_record", "table_name", "record_id"),
        Index("ix_audit_log_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<AuditLog(id={self.id}, table='{self.table_name}', "
            f"record={self.record_id}, action='{self.action}')>"
        )
