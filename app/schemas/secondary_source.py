"""Pydantic schemas for the Secondary Sources table."""

from typing import Optional

from pydantic import BaseModel, ConfigDict


class SecondarySourceBase(BaseModel):
    case_number: int
    secondary_source_link: Optional[str] = None
    secondary_source_title: Optional[str] = None


class SecondarySourceCreate(SecondarySourceBase):
    """Create a secondary source. case_number required."""
    pass


class SecondarySourceUpdate(BaseModel):
    """Update a secondary source. All fields optional."""
    case_number: Optional[int] = None
    secondary_source_link: Optional[str] = None
    secondary_source_title: Optional[str] = None


class SecondarySourceResponse(SecondarySourceBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
