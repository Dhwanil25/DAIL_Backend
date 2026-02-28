"""
Citation Extraction and Validation Service

Uses eyecite for extraction and CourtListener Citation Lookup for verification.
Processes opinion text to extract, parse, and store structured citations.
"""

import re
from typing import Optional

import structlog

from app.services.courtlistener import get_courtlistener_client

logger = structlog.get_logger()

# Common reporter abbreviations for basic extraction
# (eyecite handles comprehensive detection — this is a fallback)
COMMON_REPORTERS = [
    "F.2d", "F.3d", "F.4th", "F. Supp.", "F. Supp. 2d", "F. Supp. 3d",
    "U.S.", "S. Ct.", "L. Ed.", "L. Ed. 2d",
    "Cal.", "Cal. 2d", "Cal. 3d", "Cal. 4th", "Cal. 5th",
    "N.Y.", "N.Y.2d", "N.Y.3d",
    "A.2d", "A.3d", "N.E.2d", "N.E.3d", "N.W.2d", "P.2d", "P.3d",
    "S.E.2d", "S.W.2d", "S.W.3d", "So. 2d", "So. 3d",
]

# Regex pattern for basic volume-reporter-page citations
CITATION_PATTERN = re.compile(
    r"(\d+)\s+([A-Za-z.\s]+?)\s+(\d+)(?:\s*,\s*(\d+))?",
    re.VERBOSE,
)


class CitationService:
    """Service for citation extraction, parsing, and validation."""

    def __init__(self):
        self.cl_client = get_courtlistener_client()

    def extract_citations_basic(self, text: str) -> list[dict]:
        """
        Basic regex-based citation extraction.
        For production use, eyecite is preferred (10MB/sec throughput).
        """
        citations = []
        for match in CITATION_PATTERN.finditer(text):
            volume = match.group(1)
            reporter = match.group(2).strip()
            page = match.group(3)
            pin_cite = match.group(4)

            # Validate reporter against known list
            if any(r in reporter for r in COMMON_REPORTERS):
                citations.append({
                    "citation_text": match.group(0),
                    "volume": volume,
                    "reporter": reporter,
                    "page": page,
                    "pin_cite": pin_cite,
                })

        return citations

    def extract_citations_eyecite(self, text: str) -> list[dict]:
        """
        Extract citations using eyecite library (gold standard).
        Handles full case, short case, statutory, supra, and id citations.
        """
        try:
            from eyecite import get_citations
            from eyecite.models import (
                FullCaseCitation,
                ShortCaseCitation,
                SupraCitation,
                IdCitation,
            )

            found = get_citations(text)
            citations = []

            for cite in found:
                entry = {
                    "citation_text": str(cite),
                    "citation_type": "other",
                }

                if isinstance(cite, FullCaseCitation):
                    entry.update({
                        "citation_type": "full_case",
                        "volume": cite.groups.get("volume"),
                        "reporter": cite.corrected_reporter(),
                        "page": cite.groups.get("page"),
                        "year": cite.year,
                    })
                elif isinstance(cite, ShortCaseCitation):
                    entry.update({
                        "citation_type": "short_case",
                        "volume": cite.groups.get("volume"),
                        "reporter": cite.corrected_reporter(),
                        "page": cite.groups.get("page"),
                    })
                elif isinstance(cite, SupraCitation):
                    entry["citation_type"] = "supra"
                elif isinstance(cite, IdCitation):
                    entry["citation_type"] = "id"

                citations.append(entry)

            return citations

        except ImportError:
            logger.warning("eyecite not installed, falling back to basic extraction")
            return self.extract_citations_basic(text)

    async def verify_citation(self, citation_text: str) -> dict:
        """
        Verify a citation against CourtListener's Citation Lookup API.
        Returns the matched case data or indicates verification failure.
        """
        try:
            result = await self.cl_client.lookup_citation(citation_text)
            return {
                "verified": bool(result),
                "courtlistener_data": result,
            }
        except Exception as e:
            logger.error("Citation verification failed", error=str(e))
            return {"verified": False, "error": str(e)}

    async def extract_and_verify(self, text: str) -> list[dict]:
        """
        Full pipeline: extract citations from text, then verify each
        against CourtListener.
        """
        citations = self.extract_citations_eyecite(text)

        for citation in citations:
            if citation.get("citation_type") == "full_case":
                verification = await self.verify_citation(citation["citation_text"])
                citation["verified"] = verification.get("verified", False)
                citation["courtlistener_data"] = verification.get("courtlistener_data")

        return citations


# ── Singleton ────────────────────────────────────────────────────────────
_service: Optional[CitationService] = None


def get_citation_service() -> CitationService:
    global _service
    if _service is None:
        _service = CitationService()
    return _service
