"""Shared Pydantic schemas: pagination, generic responses."""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginationParams(BaseModel):
    skip: int = 0
    limit: int = 20


class PaginatedResponse(BaseModel, Generic[T]):
    """Wrapper for paginated list endpoints."""
    items: list[T]
    total: int
    skip: int
    limit: int


class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str
