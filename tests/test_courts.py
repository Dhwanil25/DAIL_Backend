"""
Tests for Court CRUD API endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestCourtEndpoints:

    async def test_list_courts_empty(self, client: AsyncClient):
        response = await client.get("/api/v1/courts")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []

    async def test_create_court(self, client: AsyncClient, sample_court_data):
        response = await client.post("/api/v1/courts", json=sample_court_data)
        assert response.status_code == 201
        data = response.json()
        assert data["short_name"] == "S.D.N.Y."
        assert data["jurisdiction_type"] == "federal"

    async def test_get_court_by_id(self, client: AsyncClient, sample_court_data):
        create_resp = await client.post("/api/v1/courts", json=sample_court_data)
        court_id = create_resp.json()["id"]

        response = await client.get(f"/api/v1/courts/{court_id}")
        assert response.status_code == 200
        assert "New York" in response.json()["name"]

    async def test_filter_courts_by_state(
        self, client: AsyncClient, sample_court_data
    ):
        await client.post("/api/v1/courts", json=sample_court_data)

        response = await client.get("/api/v1/courts", params={"state": "NY"})
        assert response.status_code == 200
        assert response.json()["total"] >= 1
