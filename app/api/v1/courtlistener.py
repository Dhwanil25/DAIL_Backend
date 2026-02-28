"""
CourtListener API — search and import cases from CourtListener into DAIL.

Exposes the CourtListener integration as REST endpoints so the frontend
or external tools can search, preview, and import litigation data.
"""

from datetime import date
from typing import Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import require_api_key
from app.models.case import Case
from app.models.court import Court
from app.models.docket import Docket
from app.models.party import Party, CaseParty
from app.services.courtlistener import get_courtlistener_client

router = APIRouter()


# ── Request / Response Schemas ───────────────────────────────────────────


class CLSearchRequest(BaseModel):
    """Search CourtListener for dockets or opinions."""
    query: str = Field(..., min_length=1, max_length=500, description="Search query text")
    search_type: str = Field("dockets", description="dockets or opinions")
    court: Optional[str] = Field(None, description="Court filter (e.g. 'nysd')")
    date_filed_after: Optional[str] = Field(None, description="Filter by date filed (YYYY-MM-DD)")
    page_size: int = Field(20, ge=1, le=100)


class CLSearchResult(BaseModel):
    """A single CourtListener search result."""
    courtlistener_id: Optional[int] = None
    case_name: Optional[str] = None
    docket_number: Optional[str] = None
    court: Optional[str] = None
    date_filed: Optional[str] = None
    date_terminated: Optional[str] = None
    url: Optional[str] = None
    snippet: Optional[str] = None


class CLSearchResponse(BaseModel):
    """CourtListener search response."""
    query: str
    search_type: str
    total: int = 0
    results: list[CLSearchResult] = []


class CLImportRequest(BaseModel):
    """Import a CourtListener docket into DAIL."""
    courtlistener_docket_id: int = Field(..., description="CourtListener docket ID to import")
    case_id: Optional[int] = Field(None, description="Existing DAIL case ID to link to. If null, creates a new case.")


class CLImportResponse(BaseModel):
    """Result of a CourtListener import."""
    case_id: int
    docket_id: int
    case_caption: str
    docket_number: Optional[str] = None
    courtlistener_docket_id: int
    parties_imported: int = 0
    is_new_case: bool = False
    message: str = "Import successful"


class CLDocketPreview(BaseModel):
    """Preview of a CourtListener docket before importing."""
    courtlistener_docket_id: int
    case_name: Optional[str] = None
    docket_number: Optional[str] = None
    court_name: Optional[str] = None
    court_id: Optional[str] = None
    date_filed: Optional[str] = None
    date_terminated: Optional[str] = None
    nature_of_suit: Optional[str] = None
    assigned_to: Optional[str] = None
    referred_to: Optional[str] = None
    pacer_case_id: Optional[str] = None
    cause: Optional[str] = None
    parties: list[dict] = []
    already_imported: bool = False
    existing_docket_id: Optional[int] = None


# ── Endpoints ────────────────────────────────────────────────────────────


@router.post("/search", response_model=CLSearchResponse)
async def search_courtlistener(request: CLSearchRequest):
    """
    Search CourtListener for dockets or opinions matching a query.

    This is a read-only proxy — it searches CourtListener and returns
    formatted results without saving anything to the DAIL database.
    Useful for finding cases before importing them.
    """
    client = get_courtlistener_client()

    try:
        if request.search_type == "opinions":
            data = await client.search_opinions(
                query=request.query,
                court=request.court,
                date_filed_after=request.date_filed_after,
            )
        else:
            data = await client.search_dockets(
                query=request.query,
                court=request.court,
                date_filed_after=request.date_filed_after,
            )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"CourtListener API error: {str(e)}")

    raw_results = data.get("results", [])
    total = data.get("count", len(raw_results))

    results = []
    for hit in raw_results[:request.page_size]:
        if request.search_type == "opinions":
            results.append(CLSearchResult(
                courtlistener_id=hit.get("cluster_id") or hit.get("id"),
                case_name=hit.get("caseName") or hit.get("case_name"),
                court=hit.get("court"),
                date_filed=hit.get("dateFiled") or hit.get("date_filed"),
                url=hit.get("absolute_url"),
                snippet=hit.get("snippet"),
            ))
        else:
            results.append(CLSearchResult(
                courtlistener_id=hit.get("docket_id") or hit.get("id"),
                case_name=hit.get("caseName") or hit.get("case_name"),
                docket_number=hit.get("docketNumber") or hit.get("docket_number"),
                court=hit.get("court"),
                date_filed=hit.get("dateFiled") or hit.get("date_filed"),
                date_terminated=hit.get("date_terminated"),
                url=hit.get("absolute_url"),
                snippet=hit.get("snippet"),
            ))

    return CLSearchResponse(
        query=request.query,
        search_type=request.search_type,
        total=total,
        results=results,
    )


@router.get("/preview/{courtlistener_docket_id}", response_model=CLDocketPreview)
async def preview_docket(
    courtlistener_docket_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Preview a CourtListener docket before importing it.

    Fetches full docket details from CourtListener and checks if it's
    already been imported into DAIL. Does not modify the database.
    """
    client = get_courtlistener_client()

    try:
        docket_data = await client.get_docket(courtlistener_docket_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"CourtListener API error: {str(e)}")

    # Check if already imported
    existing = await db.execute(
        select(Docket).where(Docket.courtlistener_docket_id == courtlistener_docket_id)
    )
    existing_docket = existing.scalar_one_or_none()

    # Extract parties from docket data
    parties = []
    for party in docket_data.get("parties", []):
        party_info = {
            "name": party.get("name", "Unknown"),
            "type": party.get("party_type", {}).get("name", "unknown") if isinstance(party.get("party_type"), dict) else party.get("party_type", "unknown"),
        }
        attorneys = party.get("attorneys", [])
        if attorneys:
            party_info["attorneys"] = [
                {
                    "name": att.get("attorney_name") or att.get("name", ""),
                    "firm": att.get("firm_name") or att.get("firm", ""),
                }
                for att in attorneys[:5]  # Limit to first 5 attorneys
            ]
        parties.append(party_info)

    return CLDocketPreview(
        courtlistener_docket_id=courtlistener_docket_id,
        case_name=docket_data.get("case_name"),
        docket_number=docket_data.get("docket_number"),
        court_name=docket_data.get("court_name") or (docket_data.get("court", {}).get("full_name") if isinstance(docket_data.get("court"), dict) else docket_data.get("court")),
        court_id=docket_data.get("court_id") or (docket_data.get("court", {}).get("id") if isinstance(docket_data.get("court"), dict) else None),
        date_filed=str(docket_data.get("date_filed")) if docket_data.get("date_filed") else None,
        date_terminated=str(docket_data.get("date_terminated")) if docket_data.get("date_terminated") else None,
        nature_of_suit=docket_data.get("nature_of_suit"),
        assigned_to=docket_data.get("assigned_to_str"),
        referred_to=docket_data.get("referred_to_str"),
        pacer_case_id=str(docket_data.get("pacer_case_id")) if docket_data.get("pacer_case_id") else None,
        cause=docket_data.get("cause"),
        parties=parties,
        already_imported=existing_docket is not None,
        existing_docket_id=existing_docket.id if existing_docket else None,
    )


@router.post("/import", response_model=CLImportResponse)
async def import_from_courtlistener(
    request: CLImportRequest,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(require_api_key),
):
    """
    Import a CourtListener docket into the DAIL database.

    Fetches the full docket from CourtListener, creates (or links to) a DAIL case,
    creates the docket record, and imports parties. Requires API key.

    If case_id is provided, links the docket to that existing case.
    If case_id is null, creates a new case from the docket data.
    """
    client = get_courtlistener_client()

    # Check if docket already imported
    existing = await db.execute(
        select(Docket).where(Docket.courtlistener_docket_id == request.courtlistener_docket_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail=f"Docket with CourtListener ID {request.courtlistener_docket_id} already imported"
        )

    # Fetch docket from CourtListener
    try:
        docket_data = await client.get_docket(request.courtlistener_docket_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"CourtListener API error: {str(e)}")

    case_name = docket_data.get("case_name", "Unknown Case")
    is_new_case = False

    # ── Resolve or create case ───────────────────────────────────────
    if request.case_id:
        case_result = await db.execute(select(Case).where(Case.id == request.case_id))
        case = case_result.scalar_one_or_none()
        if not case:
            raise HTTPException(status_code=404, detail=f"Case {request.case_id} not found")
    else:
        # Create new case from docket data
        case = Case(
            record_number=f"CL-{request.courtlistener_docket_id}",
            caption=case_name,
            jurisdiction_type="federal",
            status_disposition="Active",
            filed_date=_parse_date(docket_data.get("date_filed")),
            closed_date=_parse_date(docket_data.get("date_terminated")),
            keywords=docket_data.get("nature_of_suit"),
        )
        db.add(case)
        await db.flush()  # Get case.id
        is_new_case = True

    # ── Create docket ────────────────────────────────────────────────
    docket = Docket(
        case_id=case.id,
        docket_number=docket_data.get("docket_number"),
        court_name=docket_data.get("court_name") or (
            docket_data.get("court", {}).get("full_name")
            if isinstance(docket_data.get("court"), dict)
            else docket_data.get("court")
        ),
        courtlistener_docket_id=request.courtlistener_docket_id,
        courtlistener_url=f"https://www.courtlistener.com/docket/{request.courtlistener_docket_id}/",
        pacer_case_id=str(docket_data.get("pacer_case_id")) if docket_data.get("pacer_case_id") else None,
        date_filed=_parse_date(docket_data.get("date_filed")),
        date_terminated=_parse_date(docket_data.get("date_terminated")),
        nature_of_suit=docket_data.get("nature_of_suit"),
        plaintiff_summary=docket_data.get("plaintiff_summary"),
        defendant_summary=docket_data.get("defendant_summary"),
    )

    # ── Try to link to existing court ────────────────────────────────
    court_cl_id = docket_data.get("court_id") or (
        docket_data.get("court", {}).get("id")
        if isinstance(docket_data.get("court"), dict)
        else None
    )
    if court_cl_id:
        court_result = await db.execute(
            select(Court).where(Court.courtlistener_id == str(court_cl_id))
        )
        court = court_result.scalar_one_or_none()
        if court:
            docket.court_id = court.id

    db.add(docket)
    await db.flush()

    # ── Import parties ───────────────────────────────────────────────
    parties_imported = 0
    for party_data in docket_data.get("parties", []):
        try:
            party_name = party_data.get("name", "Unknown")
            party_type_raw = party_data.get("party_type")
            if isinstance(party_type_raw, dict):
                party_type = party_type_raw.get("name", "other")
            else:
                party_type = str(party_type_raw) if party_type_raw else "other"

            # Check for existing party by name
            existing_party = await db.execute(
                select(Party).where(Party.name == party_name)
            )
            party = existing_party.scalar_one_or_none()
            if not party:
                party = Party(
                    name=party_name,
                    party_type=party_type.lower() if party_type else "other",
                )
                db.add(party)
                await db.flush()

            # Link party to case
            existing_link = await db.execute(
                select(CaseParty).where(
                    CaseParty.case_id == case.id,
                    CaseParty.party_id == party.id,
                )
            )
            if not existing_link.scalar_one_or_none():
                # Get attorney info if available
                attorneys = party_data.get("attorneys", [])
                attorney_name = None
                attorney_firm = None
                if attorneys:
                    attorney_name = attorneys[0].get("attorney_name") or attorneys[0].get("name")
                    attorney_firm = attorneys[0].get("firm_name") or attorneys[0].get("firm")

                case_party = CaseParty(
                    case_id=case.id,
                    party_id=party.id,
                    role=party_type.lower() if party_type else "other",
                    attorney_name=attorney_name,
                    attorney_firm=attorney_firm,
                )
                db.add(case_party)
                parties_imported += 1

        except Exception:
            continue  # Skip problematic parties, don't fail the whole import

    await db.commit()

    return CLImportResponse(
        case_id=case.id,
        docket_id=docket.id,
        case_caption=case.caption,
        docket_number=docket.docket_number,
        courtlistener_docket_id=request.courtlistener_docket_id,
        parties_imported=parties_imported,
        is_new_case=is_new_case,
        message=f"Successfully imported docket {docket.docket_number} "
                f"({'new case created' if is_new_case else f'linked to case {case.id}'})",
    )


@router.post("/sync/{case_id}")
async def sync_case_with_courtlistener(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(require_api_key),
):
    """
    Sync an existing DAIL case with its linked CourtListener docket(s).

    Re-fetches docket data from CourtListener and updates DAIL records.
    Requires API key. The case must already have a docket with a
    courtlistener_docket_id.
    """
    # Find case and its CL-linked dockets
    case_result = await db.execute(select(Case).where(Case.id == case_id))
    case = case_result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    docket_result = await db.execute(
        select(Docket).where(
            Docket.case_id == case_id,
            Docket.courtlistener_docket_id.isnot(None),
        )
    )
    dockets = docket_result.scalars().all()
    if not dockets:
        raise HTTPException(
            status_code=404,
            detail=f"Case {case_id} has no CourtListener-linked dockets to sync"
        )

    client = get_courtlistener_client()
    synced = []

    for docket in dockets:
        try:
            docket_data = await client.get_docket(docket.courtlistener_docket_id)

            # Update docket fields
            docket.docket_number = docket_data.get("docket_number") or docket.docket_number
            docket.court_name = docket_data.get("court_name") or docket.court_name
            docket.date_filed = _parse_date(docket_data.get("date_filed")) or docket.date_filed
            docket.date_terminated = _parse_date(docket_data.get("date_terminated")) or docket.date_terminated
            docket.nature_of_suit = docket_data.get("nature_of_suit") or docket.nature_of_suit
            docket.pacer_case_id = str(docket_data.get("pacer_case_id")) if docket_data.get("pacer_case_id") else docket.pacer_case_id

            synced.append({
                "docket_id": docket.id,
                "courtlistener_docket_id": docket.courtlistener_docket_id,
                "status": "synced",
            })
        except Exception as e:
            synced.append({
                "docket_id": docket.id,
                "courtlistener_docket_id": docket.courtlistener_docket_id,
                "status": "error",
                "error": str(e),
            })

    await db.commit()

    return {
        "case_id": case_id,
        "dockets_synced": len([s for s in synced if s["status"] == "synced"]),
        "dockets_failed": len([s for s in synced if s["status"] == "error"]),
        "details": synced,
    }


# ── Helpers ──────────────────────────────────────────────────────────────


def _parse_date(date_str: Optional[str]) -> Optional[date]:
    """Parse a date string from CourtListener into a Python date object."""
    if not date_str:
        return None
    try:
        return date.fromisoformat(str(date_str)[:10])
    except (ValueError, TypeError):
        return None
