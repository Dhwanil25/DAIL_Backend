"""Pydantic schemas for the Dockets table."""

from typing import Optional

from pydantic import BaseModel, ConfigDict


class DocketBase(BaseModel):
    case_number: int
    court: Optional[str] = None
    number: Optional[str] = None
    link: Optional[str] = None


class DocketCreate(DocketBase):
    """Create a docket. case_number required."""
    pass


class DocketUpdate(BaseModel):
    """Update a docket. All fields optional."""
    case_number: Optional[int] = None
    court: Optional[str] = None
    number: Optional[str] = None
    link: Optional[str] = None


class DocketResponse(DocketBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
