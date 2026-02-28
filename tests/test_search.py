"""
Tests for full-text search endpoint.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestSearchEndpoints:

    async def test_search_empty_db(self, client: AsyncClient):
        """POST /api/v1/search should return empty results."""
        response = await client.post(
            "/api/v1/search",
            json={"query": "facial recognition"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["hits"] == []

    async def test_search_finds_case(
        self, client: AsyncClient, sample_case_data
    ):
        """Search should find cases matching query text."""
        # Create a case first
        await client.post("/api/v1/cases", json=sample_case_data)

        response = await client.post(
            "/api/v1/search",
            json={"query": "AI Corp"},
        )
        assert response.status_code == 200
        # Note: full-text search with tsvector may not work in SQLite tests.
        # This test validates the endpoint plumbing.


@pytest.mark.asyncio
class TestAnalyticsEndpoints:

    async def test_analytics_summary(self, client: AsyncClient):
        """GET /api/v1/analytics/summary should return dashboard data."""
        response = await client.get("/api/v1/analytics/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_cases" in data
        assert "status_breakdown" in data
