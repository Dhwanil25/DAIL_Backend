"""
Pagination utilities.
"""

from typing import Generic, TypeVar, Sequence

from pydantic import BaseModel

T = TypeVar("T")


def paginate_query(query, page: int, page_size: int):
    """Apply offset/limit pagination to a SQLAlchemy query."""
    offset = (page - 1) * page_size
    return query.offset(offset).limit(page_size)


def calculate_total_pages(total: int, page_size: int) -> int:
    """Calculate total pages from total items and page size."""
    if total == 0:
        return 1
    return (total + page_size - 1) // page_size
