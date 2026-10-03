"""
API Contract and Integration Tests (Layer 8).
Tests:
  1. Export endpoint for CSV, JSON, GeoJSON, and Parquet.
  2. Lineage endpoint tracing evidence units and fallback levels.
  3. Webhooks subscription and test event delivery.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_export_endpoints_all_formats(client: AsyncClient):
    """Verify /export endpoint supports CSV, JSON, GeoJSON, Parquet."""
    # 1. CSV
    csv_res = await client.get("/api/v1/export?format=csv")
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers.get("content-type", "")
    assert "district_name" in csv_res.text
    assert "data_mode" in csv_res.text

    # 2. JSON
    json_res = await client.get("/api/v1/export?format=json")
    assert json_res.status_code == 200
    data = json_res.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "gap_status" in data[0]

    # 3. GeoJSON
    geo_res = await client.get("/api/v1/export?format=geojson")
    assert geo_res.status_code == 200
    geo_data = geo_res.json()
    assert geo_data.get("type") == "FeatureCollection"
    assert "features" in geo_data
    assert len(geo_data["features"]) > 0

    # 4. Parquet
    p_res = await client.get("/api/v1/export?format=parquet")
    assert p_res.status_code == 200
    assert "application/octet-stream" in p_res.headers.get("content-type", "")
    assert len(p_res.content) > 100


@pytest.mark.asyncio
async def test_lineage_endpoint(client: AsyncClient):
    """Verify /lineage/{cell_id} returns evidence units, weights, and stages."""
    res = await client.get("/api/v1/lineage/1_1")
    assert res.status_code == 200
    data = res.json()
    assert data["cell_id"] == "1_1"
    assert "evidence_units" in data
    assert len(data["evidence_units"]) > 0
    assert "fallback_level" in data
    assert "pipeline_stages" in data
    assert data["data_mode"] == "synthetic"


@pytest.mark.asyncio
async def test_webhooks_pipeline(client: AsyncClient):
    """Verify webhook registration, listing, and test delivery."""
    # 1. Subscribe
    sub_payload = {
        "target_url": "https://example.com/webhook",
        "events": ["alert.created", "alert.escalated"],
        "state_code": "KA",
    }
    sub_res = await client.post("/api/v1/webhooks", json=sub_payload)
    assert sub_res.status_code == 200
    wh_data = sub_res.json()
    assert "webhook_id" in wh_data
    wh_id = wh_data["webhook_id"]

    # 2. List
    list_res = await client.get("/api/v1/webhooks")
    assert list_res.status_code == 200
    subs = list_res.json()
    assert any(s["webhook_id"] == wh_id for s in subs)

    # 3. Test delivery
    test_res = await client.post(f"/api/v1/webhooks/test?webhook_id={wh_id}")
    assert test_res.status_code == 200
    test_data = test_res.json()
    assert test_data["delivered"] is True
    assert test_data["event_type"] == "alert.escalated"
    assert "transition" in test_data["payload"]
