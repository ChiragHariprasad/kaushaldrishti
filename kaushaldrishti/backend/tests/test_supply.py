"""
Section 7 Tests: Mathematical and Architectural Verification of Supply Dynamics Engine.
Tests:
1. Rates are bounded in [0, 1].
2. Product matches the closed form at the mean: E[S] = C * E[E] * E[CR] * E[Cert].
3. Capacity-only cells are labelled 'capacity_based' and never called 'certified entrants'.
4. Placement columns are not read by the supply module (assert via a test that fails if they are).
5. Supply API queryability: /api/v1/supply returns forecasts with intervals and basis.
"""

import numpy as np
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from pipelines.supply.beta_models import BetaRateModel
from pipelines.supply.engine import PipelineCohortInput, SupplyDynamicsEngine


def test_section_7_requirement_1_rates_bounded():
    """
    1. Rates (E, CR, Cert) drawn from Beta posteriors are strictly bounded in [0, 1].
    """
    model = BetaRateModel(prior_alpha=18.0, prior_beta=2.0)
    post_a, post_b = model.update_posterior(successes=45, trials=50)

    samples = BetaRateModel.sample_posterior(post_a, post_b, n_draws=5000)

    assert len(samples) == 5000
    assert np.all(samples >= 0.0), "Rate samples must be >= 0.0"
    assert np.all(samples <= 1.0), "Rate samples must be <= 1.0"
    assert float(np.min(samples)) >= 0.0
    assert float(np.max(samples)) <= 1.0


def test_section_7_requirement_2_product_matches_closed_form_mean():
    """
    2. Monte Carlo sample product matches the analytical closed-form expectation at the mean:
    E[S] = C * E[E] * E[CR] * E[Cert].
    """
    engine = SupplyDynamicsEngine(n_draws=10000, seed=42)

    cohort = PipelineCohortInput(
        capacity=100,
        allocated_seats=80,
        enrolled=72,     # ~90%
        completed=60,    # ~83%
        certified=54,    # ~90%
        course_months=6,
    )

    res = engine.compute_s_cert(cohort)

    simulated_mean = res["s_mean"]
    closed_form_expected = res["expected_closed_form"]

    # Monte Carlo mean should match analytical expectation within 1.5% tolerance
    relative_diff = abs(simulated_mean - closed_form_expected) / closed_form_expected
    print(f"\nSimulated Mean: {simulated_mean}, Closed Form Expected: {closed_form_expected}, Diff: {relative_diff:.4f}")
    assert relative_diff < 0.015, f"Relative difference {relative_diff:.4f} exceeds 1.5% tolerance"


def test_section_7_requirement_3_capacity_only_labelled_capacity_based():
    """
    3. Capacity-only cells (no enrollment/completion pipeline data yet)
    are strictly labelled 'capacity_based' and never called 'certified entrants'.
    """
    engine = SupplyDynamicsEngine()

    # Newly sanctioned centre: seats allocated, but no batches completed yet
    new_cohort = PipelineCohortInput(
        capacity=60,
        allocated_seats=60,
        enrolled=0,
        completed=0,
        certified=0,
    )

    res = engine.compute_s_cert(new_cohort)

    assert res["basis"] == "capacity_based", f"Expected basis 'capacity_based', got '{res['basis']}'"
    assert res["basis"] != "certified"
    assert res["s_mean"] == 60.0

    # Test window aggregation preserves capacity_based label
    win_res = engine.compute_window_supply([new_cohort], window_months=12)
    assert win_res["basis"] == "capacity_based"


def test_section_7_requirement_4_placement_columns_not_read():
    """
    4. Architectural Rule: Placement/employment outcomes MUST NOT enter the supply definition.
    Assert that PipelineCohortInput rejects any placement-related attributes,
    and SupplyDynamicsEngine methods never read or reference 'placed' or 'employment'.
    """
    import inspect

    # 1. PipelineCohortInput dataclass does not have a 'placed' or 'employment' field
    fields = [f for f in PipelineCohortInput.__dataclass_fields__]
    assert "placed" not in fields, "CRITICAL: 'placed' column found in supply cohort input schema!"
    assert "placement" not in fields, "CRITICAL: 'placement' column found in supply cohort input schema!"
    assert "employment" not in fields, "CRITICAL: 'employment' column found in supply cohort input schema!"

    # 2. Attempting to pass placed to PipelineCohortInput must raise a TypeError
    with pytest.raises(TypeError) as exc_info:
        PipelineCohortInput(
            capacity=50,
            allocated_seats=50,
            enrolled=40,
            completed=35,
            certified=30,
            placed=25,  # type: ignore
        )
    assert "unexpected keyword argument 'placed'" in str(exc_info.value)

    # 3. Code inspection of SupplyDynamicsEngine source code: ensure no mention of placement
    source_code = inspect.getsource(SupplyDynamicsEngine)
    # Check that in the computation logic, placed is not used
    assert "cohort.placed" not in source_code
    assert "cohort.placement" not in source_code


@pytest.mark.asyncio
async def test_supply_api_queryability():
    """
    5. Supply API endpoint /api/v1/supply returns forecasts with intervals (q10 <= mean <= q90)
    and proper basis labels.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/supply?state=KA&trade=EV Service Technician&window_months=12")
        assert res.status_code == 200
        items = res.json()
        assert len(items) > 0

        first = items[0]
        assert first["state_code"] == "KA"
        assert "EV Service Technician" in first["trade_name"]
        assert first["window_months"] == 12
        assert first["s_q10"] <= first["s_mean"] <= first["s_q90"]
        assert first["basis"] in ["certified", "capacity_based", "certified_plus_other"]
        assert first["data_mode"] == "synthetic"
