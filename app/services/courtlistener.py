"""
CourtListener API Integration Service

Provides a robust, rate-limited client for the CourtListener REST API (v4.4).
Handles authentication, pagination, caching, and retry logic.

API Docs: https://www.courtlistener.com/api/rest-info/
Rate Limit: 5,000 queries/hour for authenticated users.
"""

import asyncio
from datetime import datetime
from typing import Any, Optional

import httpx
import structlog

from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class CourtListenerClient:
    """Async client for CourtListener REST API v4."""

    BASE_URL = settings.COURTLISTENER_BASE_URL

    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or settings.COURTLISTENER_API_TOKEN
        self.headers = {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json",
        }
        self._request_count = 0
        self._window_start = datetime.utcnow()

    async def _get_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers=self.headers,
            timeout=30.0,
        )

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        retries: int = 3,
    ) -> dict[str, Any]:
        """Make a rate-limited request with retries."""
        for attempt in range(retries):
            try:
                async with await self._get_client() as client:
                    response = await client.request(
                        method, endpoint, params=params, json=data
                    )

                    if response.status_code == 429:
                        retry_after = int(response.headers.get("Retry-After", 60))
                        logger.warning(
                            "CourtListener rate limited",
                            retry_after=retry_after,
                            attempt=attempt + 1,
                        )
                        await asyncio.sleep(retry_after)
                        continue

                    response.raise_for_status()
                    self._request_count += 1
                    return response.json()

            except httpx.HTTPStatusError as e:
                logger.error(
                    "CourtListener API error",
                    status=e.response.status_code,
                    detail=str(e),
                    attempt=attempt + 1,
                )
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)

            except httpx.RequestError as e:
                logger.error(
                    "CourtListener connection error",
                    error=str(e),
                    attempt=attempt + 1,
                )
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)

        raise RuntimeError("CourtListener request failed after all retries")

    # ── Docket Endpoints ─────────────────────────────────────────────

    async def get_docket(self, docket_id: int) -> dict:
        """Fetch a docket by CourtListener ID."""
        return await self._request("GET", f"/dockets/{docket_id}/")

    async def search_dockets(
        self,
        query: str,
        court: Optional[str] = None,
        date_filed_after: Optional[str] = None,
        cursor: Optional[str] = None,
    ) -> dict:
        """Search dockets with keyword and filters."""
        params: dict[str, Any] = {"q": query, "type": "d"}
        if court:
            params["court"] = court
        if date_filed_after:
            params["date_filed__gte"] = date_filed_after
        if cursor:
            params["cursor"] = cursor
        return await self._request("GET", "/search/", params=params)

    # ── Opinion Endpoints ────────────────────────────────────────────

    async def get_cluster(self, cluster_id: int) -> dict:
        """Fetch an opinion cluster by ID."""
        return await self._request("GET", f"/clusters/{cluster_id}/")

    async def get_opinion(self, opinion_id: int) -> dict:
        """Fetch a single opinion by ID."""
        return await self._request("GET", f"/opinions/{opinion_id}/")

    async def search_opinions(
        self,
        query: str,
        court: Optional[str] = None,
        date_filed_after: Optional[str] = None,
    ) -> dict:
        """Search opinions."""
        params: dict[str, Any] = {"q": query, "type": "o"}
        if court:
            params["court"] = court
        if date_filed_after:
            params["date_filed__gte"] = date_filed_after
        return await self._request("GET", "/search/", params=params)

    # ── RECAP Document Endpoints ─────────────────────────────────────

    async def get_recap_document(self, rd_id: int) -> dict:
        """Fetch a RECAP document."""
        return await self._request("GET", f"/recap-documents/{rd_id}/")

    async def search_recap(
        self,
        query: str,
        docket_id: Optional[int] = None,
    ) -> dict:
        """Search RECAP documents."""
        params: dict[str, Any] = {"q": query, "type": "r"}
        if docket_id:
            params["docket_id"] = docket_id
        return await self._request("GET", "/search/", params=params)

    # ── Citation Endpoints ───────────────────────────────────────────

    async def lookup_citation(self, citation_text: str) -> dict:
        """
        Use the Citation Lookup endpoint to verify a citation.
        This is the anti-hallucination tool.
        """
        return await self._request(
            "POST", "/citation-lookup/", data={"text": citation_text}
        )

    async def get_citations(
        self,
        citing_opinion_id: Optional[int] = None,
        cited_opinion_id: Optional[int] = None,
    ) -> dict:
        """Fetch citation links."""
        params: dict[str, Any] = {}
        if citing_opinion_id:
            params["citing_opinion"] = citing_opinion_id
        if cited_opinion_id:
            params["cited_opinion"] = cited_opinion_id
        return await self._request("GET", "/citations/", params=params)

    # ── People/Judges Endpoints ──────────────────────────────────────

    async def get_person(self, person_id: int) -> dict:
        """Fetch judge biographical data."""
        return await self._request("GET", f"/people/{person_id}/")

    async def search_people(self, name: str) -> dict:
        """Search for judges/people."""
        return await self._request("GET", "/people/", params={"name": name})

    # ── Court Endpoints ──────────────────────────────────────────────

    async def get_court(self, court_id: str) -> dict:
        """Fetch court data by CourtListener court ID."""
        return await self._request("GET", f"/courts/{court_id}/")

    async def list_courts(self) -> dict:
        """List all courts."""
        return await self._request("GET", "/courts/")

    # ── Search Alerts (for automated ingestion) ──────────────────────

    async def create_search_alert(
        self,
        name: str,
        query: str,
        search_type: str = "o",
        rate: str = "rt",  # real-time
    ) -> dict:
        """Create a search alert for automated case detection."""
        return await self._request(
            "POST",
            "/alerts/",
            data={
                "name": name,
                "query": query,
                "type": search_type,
                "rate": rate,
            },
        )

    # ── Pagination Helper ────────────────────────────────────────────

    async def paginate_all(
        self,
        endpoint: str,
        params: Optional[dict] = None,
        max_pages: int = 100,
    ) -> list[dict]:
        """Iterate through all pages of a cursor-paginated endpoint."""
        all_results = []
        current_params = params or {}

        for _ in range(max_pages):
            data = await self._request("GET", endpoint, params=current_params)
            results = data.get("results", [])
            all_results.extend(results)

            next_url = data.get("next")
            if not next_url:
                break

            # Extract cursor from next URL
            if "cursor=" in next_url:
                cursor = next_url.split("cursor=")[1].split("&")[0]
                current_params["cursor"] = cursor

        return all_results


# ── Singleton ────────────────────────────────────────────────────────────
_client: Optional[CourtListenerClient] = None


def get_courtlistener_client() -> CourtListenerClient:
    """Get or create the CourtListener client singleton."""
    global _client
    if _client is None:
        _client = CourtListenerClient()
    return _client
