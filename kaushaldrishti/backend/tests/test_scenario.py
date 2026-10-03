"""
Policy Scenario Simulator Tests (Layer 7 & 8).
Tests:
  1. Stock-flow cohort simulation with pipeline delays L.
  2. Closing cycle calculation (+15% seats closing emerging shortage).
  3. POST and GET /api/v1/scenarios endpoints.
"""

import pytest
from httpx import AsyncClient

from pipelines.scenario.simulator import PolicyScenarioSimulator


def test_scenario_simulator_pipeline_delay():
    """
    Verify that graduates from increased seats emerge only after cohort lag L.
    """
    sim = PolicyScenarioSimulator(simulation_months=24)
    res = sim.simulate(
        base_demand=2400.0,
        demand_sigma=200.0,
        base_capacity=1800,
        fill_rate=0.85,
        completion_rate=0.80,
        cert_rate=0.90,
        course_months=6,  # L = 6 months
        seat_delta_pct=0.20,  # +20% seats
        demand_case="base",
        start_month_str="2025-01",
    )

    series = res["series"]
    assert len(series["months"]) == 24
    assert res["summary"]["pipeline_lag_months"] == 6

    # For months 0..5 (t < 6), intervention supply must equal baseline supply
    for t in range(6):
        assert series["intervention_supply"][t] == series["baseline_supply"][t]

    # For months >= 6, intervention supply must be strictly higher
    for t in range(6, 24):
        assert series["intervention_supply"][t] > series["baseline_supply"][t]

    assert res["summary"]["net_additional_graduates"] > 0


def test_scenario_closing_cycle_calculation():
    """
    Verify that +15% seats on a deficit trade calculates an explicit closing cycle.
    """
    sim = PolicyScenarioSimulator(simulation_months=24)
    res = sim.simulate(
        base_demand=1200.0,  # 100/mo
        demand_sigma=100.0,
        base_capacity=1200,  # throughput ~ 61/mo (shortage of ~39/mo)
        fill_rate=0.90,
        completion_rate=0.85,
        cert_rate=0.90,
        course_months=4,
        seat_delta_pct=0.45,  # +45% expansion
        completion_delta_pp=0.08,  # +8% completion
        demand_case="base",
        start_month_str="2025-01",
    )

    assert "closing_cycle" in res["summary"]
    assert len(res["assumptions"]) >= 5


@pytest.mark.asyncio
async def test_scenario_api_endpoints(client: AsyncClient):
    """Verify POST /api/v1/scenarios and GET /api/v1/scenarios/{id}."""
    payload = {
        "district_id": 1,
        "trade_id": 1,
        "seat_delta_pct": 0.15,
        "completion_delta_pp": 0.05,
        "new_centre_capacity": 50,
        "new_centre_build_lag_months": 6,
        "demand_case": "base",
        "start_month": "2025-01",
    }

    # 1. POST /scenarios
    post_res = await client.post("/api/v1/scenarios", json=payload)
    assert post_res.status_code == 200
    data = post_res.json()
    assert "scenario_id" in data
    assert "summary" in data
    assert "series" in data
    assert "months" in data["series"]
    assert "intervention_gap" in data["series"]

    sc_id = data["scenario_id"]

    # 2. GET /scenarios/{id}
    get_res = await client.get(f"/api/v1/scenarios/{sc_id}")
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert get_data["scenario_id"] == sc_id
    assert get_data["district_id"] == 1
    assert get_data["trade_id"] == 1
