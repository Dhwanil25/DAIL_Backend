"""
Data validators for legal data integrity.
"""

import re
from datetime import date
from typing import Optional


def validate_docket_number(docket_number: str) -> bool:
    """
    Validate a federal court docket number format.
    Common formats: 1:23-cv-12345, 23-cv-12345-ABC
    """
    pattern = r"^\d{1,2}:\d{2}-[a-z]{2,3}-\d{4,6}(-[A-Z]+)?$"
    return bool(re.match(pattern, docket_number, re.IGNORECASE))


def normalize_docket_number(docket_number: str) -> str:
    """
    Normalize a docket number to a standard format.
    Strips spaces, standardizes separators.
    """
    normalized = docket_number.strip()
    normalized = re.sub(r"\s+", "", normalized)
    return normalized


def validate_citation_format(citation: str) -> bool:
    """
    Basic validation that a string looks like a legal citation.
    E.g., '123 F.3d 456'
    """
    pattern = r"\d+\s+[A-Za-z.\s]+\d+"
    return bool(re.match(pattern, citation.strip()))


def validate_date_range(
    start_date: Optional[date], end_date: Optional[date]
) -> bool:
    """Validate that start_date <= end_date if both are provided."""
    if start_date and end_date:
        return start_date <= end_date
    return True


def sanitize_search_query(query: str) -> str:
    """
    Sanitize a search query for use in PostgreSQL tsquery.
    Removes special characters that could break the query.
    """
    # Remove characters that have special meaning in tsquery
    sanitized = re.sub(r"[!&|():<>]", " ", query)
    # Collapse multiple spaces
    sanitized = re.sub(r"\s+", " ", sanitized).strip()
    return sanitized
