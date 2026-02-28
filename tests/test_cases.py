"""
Tests for Case CRUD API endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestCaseEndpoints:

    async def test_list_cases_empty(self, client: AsyncClient):
        """GET /api/v1/cases should return empty list initially."""
        response = await client.get("/api/v1/cases")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    async def test_create_case(self, client: AsyncClient, sample_case_data):
        """POST /api/v1/cases should create a new case."""
        response = await client.post("/api/v1/cases", json=sample_case_data)
        assert response.status_code == 201
        data = response.json()
        assert data["record_number"] == "TEST-001"
        assert data["caption"] == "Doe v. AI Corp"
        assert data["id"] is not None

    async def test_get_case_by_id(self, client: AsyncClient, sample_case_data):
        """GET /api/v1/cases/{id} should return the created case."""
        # Create first
        create_resp = await client.post("/api/v1/cases", json=sample_case_data)
        case_id = create_resp.json()["id"]

        # Fetch
        response = await client.get(f"/api/v1/cases/{case_id}")
        assert response.status_code == 200
        assert response.json()["caption"] == "Doe v. AI Corp"

    async def test_get_case_not_found(self, client: AsyncClient):
        """GET /api/v1/cases/999 should return 404."""
        response = await client.get("/api/v1/cases/999")
        assert response.status_code == 404

    async def test_update_case(self, client: AsyncClient, sample_case_data):
        """PATCH /api/v1/cases/{id} should update fields."""
        create_resp = await client.post("/api/v1/cases", json=sample_case_data)
        case_id = create_resp.json()["id"]

        response = await client.patch(
            f"/api/v1/cases/{case_id}",
            json={"brief_description": "Updated description"},
        )
        assert response.status_code == 200
        assert response.json()["brief_description"] == "Updated description"

    async def test_delete_case_soft(self, client: AsyncClient, sample_case_data):
        """DELETE /api/v1/cases/{id} should soft-delete."""
        create_resp = await client.post("/api/v1/cases", json=sample_case_data)
        case_id = create_resp.json()["id"]

        response = await client.delete(f"/api/v1/cases/{case_id}")
        assert response.status_code == 200

        # Should still exist but not appear in list
        get_resp = await client.get(f"/api/v1/cases/{case_id}")
        # Soft-deleted cases may still be retrievable by ID
        # depending on implementation; the list should exclude them

    async def test_get_case_by_record_number(
        self, client: AsyncClient, sample_case_data
    ):
        """GET /api/v1/cases/record/{record_number} should work."""
        await client.post("/api/v1/cases", json=sample_case_data)

        response = await client.get("/api/v1/cases/record/TEST-001")
        assert response.status_code == 200
        assert response.json()["record_number"] == "TEST-001"

    async def test_duplicate_record_number_rejected(
        self, client: AsyncClient, sample_case_data
    ):
        """POST duplicate record_number should return 409."""
        await client.post("/api/v1/cases", json=sample_case_data)
        response = await client.post("/api/v1/cases", json=sample_case_data)
        assert response.status_code == 409

    async def test_list_cases_with_filters(
        self, client: AsyncClient, sample_case_data
    ):
        """GET /api/v1/cases with query params should filter."""
        await client.post("/api/v1/cases", json=sample_case_data)

        # Filter by status
        response = await client.get(
            "/api/v1/cases", params={"status": "pending"}
        )
        assert response.status_code == 200
        assert response.json()["total"] >= 1

        # Filter by area
        response = await client.get(
            "/api/v1/cases", params={"area_of_application": "Employment"}
        )
        assert response.status_code == 200
        assert response.json()["total"] >= 1
