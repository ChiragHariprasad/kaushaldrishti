"""
Tests for health and metadata endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    """Health endpoint returns 200 with expected fields."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"
    assert "uptime_seconds" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_metadata_endpoint():
    """Metadata endpoint returns pilot scope and data_mode counts."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/metadata")

    assert response.status_code == 200
    data = response.json()
    assert data["app_name"] == "KaushalDrishti"
    assert len(data["pilot_states"]) == 3
    assert "Karnataka" in data["pilot_states"]
    assert len(data["pilot_sectors"]) == 5
    assert len(data["languages"]) == 4
    assert set(data["data_mode_counts"].keys()) == {
        "live", "public_aggregate", "partner", "synthetic"
    }


@pytest.mark.asyncio
async def test_openapi_available():
    """OpenAPI spec is served at the expected path."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/openapi.json")

    assert response.status_code == 200
    spec = response.json()
    assert spec["info"]["title"] == "KaushalDrishti API"


@pytest.mark.asyncio
async def test_quality_endpoint():
    """Quality scorecard endpoint returns per-source metrics."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/quality")

    assert response.status_code == 200
    data = response.json()
    assert data["overall_health"] == "healthy"
    assert len(data["sources"]) >= 4
    ncs_card = next(s for s in data["sources"] if s["source_id"] == "ncs")
    assert ncs_card["data_mode"] == "synthetic"
    assert ncs_card["reliability_r_k"] > 0


@pytest.mark.asyncio
async def test_review_queue_endpoint():
    """Review queue endpoint returns pending mapping items and accepts decisions."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. List pending
        response = await client.get("/api/v1/review-queue")
        assert response.status_code == 200
        items = response.json()
        assert len(items) > 0
        first_id = items[0]["id"]

        # 2. Decide item
        decide_res = await client.post(
            f"/api/v1/review-queue/{first_id}/decide",
            json={"decision": "approved", "reviewer_notes": "Verified mapping"},
        )
        assert decide_res.status_code == 200
        dec_data = decide_res.json()
        assert dec_data["new_status"] == "approved"
