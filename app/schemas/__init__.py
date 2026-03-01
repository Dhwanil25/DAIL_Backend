"""
DAIL Backend - Pydantic Schemas

Re-exports all schema classes for convenient imports.
"""

from app.schemas.common import (
    ErrorResponse,
    MessageResponse,
    PaginatedResponse,
    PaginationParams,
)
from app.schemas.case import (
    CaseBase,
    CaseCreate,
    CaseDetailResponse,
    CaseResponse,
    CaseUpdate,
)
from app.schemas.docket import (
    DocketBase,
    DocketCreate,
    DocketResponse,
    DocketUpdate,
)
from app.schemas.document import (
    DocumentBase,
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
)
from app.schemas.secondary_source import (
    SecondarySourceBase,
    SecondarySourceCreate,
    SecondarySourceResponse,
    SecondarySourceUpdate,
)

__all__ = [
    "ErrorResponse",
    "MessageResponse",
    "PaginatedResponse",
    "PaginationParams",
    "CaseBase",
    "CaseCreate",
    "CaseDetailResponse",
    "CaseResponse",
    "CaseUpdate",
    "DocketBase",
    "DocketCreate",
    "DocketResponse",
    "DocketUpdate",
    "DocumentBase",
    "DocumentCreate",
    "DocumentResponse",
    "DocumentUpdate",
    "SecondarySourceBase",
    "SecondarySourceCreate",
    "SecondarySourceResponse",
    "SecondarySourceUpdate",
]
