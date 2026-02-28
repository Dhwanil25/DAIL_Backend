"""
Ingestion Service — data import pipeline from CourtListener and Caspio exports.

Handles:
- Caspio XLSX migration
- CourtListener docket enrichment
- Automated new case detection
"""

from datetime import datetime
from typing import Any, Optional

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.models.docket import Docket
from app.models.document import Document
from app.models.secondary_source import SecondarySource
from app.models.provenance import Provenance
from app.services.courtlistener import get_courtlistener_client
from app.services.classification_service import get_classification_service

logger = structlog.get_logger()


class IngestionService:
    """Service for data import and enrichment."""

    def __init__(self):
        self.cl_client = get_courtlistener_client()
        self.classifier = get_classification_service()

    # ── Caspio Migration ─────────────────────────────────────────────

    async def import_caspio_case(
        self, row: dict[str, Any], db: AsyncSession
    ) -> Case:
        """
        Import a single case from Caspio export data.
        Handles field mapping and provenance recording.
        """
        # Map Caspio status to our enum
        caspio_status = (row.get("status_disposition") or "").lower()
        mapped_status = self._map_caspio_status(caspio_status)

        case = Case(
            record_number=row.get("record_number"),
            caption=row.get("caption", "Unknown Case"),
            case_slug=row.get("case_slug"),
            brief_description=row.get("brief_description"),
            area_of_application=row.get("area_of_application"),
            issue_text=row.get("issue_text"),
            cause_of_action=row.get("cause_of_action"),
            algorithm_name=row.get("algorithm_name"),
            is_class_action=bool(row.get("is_class_action")),
            organizations_involved=row.get("organizations_involved"),
            jurisdiction_name=row.get("jurisdiction_name"),
            jurisdiction_type=row.get("jurisdiction_type"),
            jurisdiction_state=row.get("jurisdiction_state"),
            jurisdiction_municipality=row.get("jurisdiction_municipality"),
            status_disposition=row.get("status_disposition"),
            filed_date=row.get("filed_date"),
            closed_date=row.get("closed_date"),
            facts=row.get("facts"),
            keywords=row.get("keywords"),
        )

        db.add(case)
        await db.flush()

        # Auto-classify the case
        classification = self.classifier.classify_case(
            caption=case.caption,
            description=case.brief_description or "",
            issues=case.issue_text or "",
            cause_of_action=case.cause_of_action or "",
        )
        case.ai_technology_types = classification["ai_technology_types"]
        case.legal_theories = classification["legal_theories"]
        case.industry_sectors = classification["industry_sectors"]

        # Record provenance
        provenance = Provenance(
            case_id=case.id,
            source_system="caspio_migration",
            ingestion_method="xlsx_import",
            source_identifier=str(row.get("record_number")),
        )
        db.add(provenance)

        logger.info(
            "Imported case from Caspio",
            case_id=case.id,
            record_number=case.record_number,
            caption=case.caption[:80],
        )

        return case

    async def import_caspio_docket(
        self, row: dict[str, Any], case_id: int, db: AsyncSession
    ) -> Docket:
        """Import a docket entry from Caspio data."""
        docket = Docket(
            case_id=case_id,
            docket_number=row.get("docket_number"),
            court_name=row.get("court"),
            courtlistener_url=row.get("link"),
        )
        db.add(docket)
        await db.flush()
        return docket

    async def import_caspio_document(
        self, row: dict[str, Any], case_id: int, db: AsyncSession
    ) -> Document:
        """Import a document from Caspio data."""
        doc = Document(
            case_id=case_id,
            document_title=row.get("document_title"),
            document_date=row.get("document_date"),
            link=row.get("link"),
            cite_or_reference=row.get("cite_or_reference"),
        )
        db.add(doc)
        await db.flush()
        return doc

    async def import_caspio_secondary_source(
        self, row: dict[str, Any], case_id: int, db: AsyncSession
    ) -> SecondarySource:
        """Import a secondary source from Caspio data."""
        source = SecondarySource(
            case_id=case_id,
            title=row.get("secondary_source_title"),
            link=row.get("secondary_source_link"),
        )
        db.add(source)
        await db.flush()
        return source

    # ── CourtListener Enrichment ─────────────────────────────────────

    async def enrich_case_from_courtlistener(
        self, case_id: int, docket_url: str, db: AsyncSession
    ) -> dict:
        """
        Enrich a DAIL case with data from CourtListener.
        Extracts docket metadata, party info, and filing details.
        """
        try:
            # Extract CL docket ID from URL
            cl_docket_id = self._extract_cl_docket_id(docket_url)
            if not cl_docket_id:
                return {"status": "error", "message": "Could not parse CourtListener URL"}

            # Fetch from CourtListener
            cl_data = await self.cl_client.get_docket(cl_docket_id)

            # Update the docket with enriched data
            result = await db.execute(
                select(Docket).where(
                    Docket.case_id == case_id,
                    Docket.courtlistener_url.contains(str(cl_docket_id)),
                )
            )
            docket = result.scalar_one_or_none()

            if docket:
                docket.courtlistener_docket_id = cl_docket_id
                docket.date_filed = cl_data.get("date_filed")
                docket.date_terminated = cl_data.get("date_terminated")
                docket.nature_of_suit = cl_data.get("nature_of_suit")
                docket.pacer_case_id = cl_data.get("pacer_case_id")

            # Record provenance
            provenance = Provenance(
                case_id=case_id,
                source_system="courtlistener_api",
                ingestion_method="api_pull",
                source_url=f"https://www.courtlistener.com/api/rest/v4/dockets/{cl_docket_id}/",
                source_identifier=str(cl_docket_id),
            )
            db.add(provenance)

            return {
                "status": "success",
                "docket_id": cl_docket_id,
                "data_enriched": True,
            }

        except Exception as e:
            logger.error(
                "CourtListener enrichment failed",
                case_id=case_id,
                error=str(e),
            )
            return {"status": "error", "message": str(e)}

    # ── Helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _map_caspio_status(status_text: str) -> str:
        """Map Caspio status text to a status string."""
        mapping = {
            "filed": "filed",
            "active": "active",
            "pending": "active",
            "settled": "settled",
            "dismissed": "dismissed",
            "judgment": "judgment",
            "appeal": "on_appeal",
            "on appeal": "on_appeal",
            "closed": "closed",
            "consolidated": "consolidated",
            "transferred": "transferred",
        }

        for key, value in mapping.items():
            if key in status_text:
                return value

        return "unknown"

    @staticmethod
    def _extract_cl_docket_id(url: str) -> Optional[int]:
        """Extract CourtListener docket ID from a CourtListener URL."""
        import re
        match = re.search(r"/docket/(\d+)/", url)
        if match:
            return int(match.group(1))
        return None


# ── Singleton ────────────────────────────────────────────────────────────
_service: Optional[IngestionService] = None


def get_ingestion_service() -> IngestionService:
    global _service
    if _service is None:
        _service = IngestionService()
    return _service
