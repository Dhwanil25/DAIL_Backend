"""
Common schemas — shared pagination, response wrappers, and enums.
"""

from datetime import datetime
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


# ── Pagination ───────────────────────────────────────────────────────────
class PaginationParams(BaseModel):
    """Query parameters for paginated endpoints."""
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response envelope."""
    items: list[T]
    total: int = Field(description="Total number of items matching query")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Items per page")
    total_pages: int = Field(description="Total number of pages")

    @classmethod
    def create(cls, items: list[T], total: int, page: int, page_size: int) -> "PaginatedResponse[T]":
        total_pages = max(1, (total + page_size - 1) // page_size)
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


# ── Standard API Responses ───────────────────────────────────────────────
class MessageResponse(BaseModel):
    """Simple message response."""
    message: str
    detail: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
    status_code: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    version: str = "1.0.0"
    database: str = "unknown"
    redis: str = "unknown"
    timestamp: datetime


# ── Sort Options ─────────────────────────────────────────────────────────
class SortOrder(BaseModel):
    """Sort field and direction."""
    field: str = "created_at"
    direction: str = Field("desc", pattern="^(asc|desc)$")
