"""
Section 5 Tests: Mathematical Verification of Kalman Demand Intelligence Engine.
Tests:
(a) With one source and tau -> infinity, the posterior equals that source.
(b) With identical sources, posterior variance falls as 1/n.
(c) Source contributions plus prior share sum to the total change.
(d) A source made artificially noisy gets its r_k reduced and its weight cut.
(e) A stale source is gated out.
Plus: Verification that a cell's LDI, interval, confidence, and source contributions are queryable via the API.
"""

import math
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from pipelines.demand.gate import ReliabilityGate
from pipelines.demand.kalman import KalmanFusion
from pipelines.demand.index import DemandIndexEngine
from pipelines.signals.evidence import EvidenceUnitBuilder


def test_section_5_property_a_single_source_tau_infinity():
    """
    (a) With one source and tau -> infinity (no shrinkage to state prior),
    the update with diffuse prior equals that source observation z.
    """
    kf = KalmanFusion()
    # Diffuse prior (large variance, zero information)
    m_prior = 0.0
    p_prior = 1e6

    z_obs = 4.85
    v_obs = 0.12

    update = kf.update(
        m_prior, p_prior,
        [{"source_id": "test_src", "z": z_obs, "v": v_obs, "gate_pass": True}],
    )

    # Posterior mean must equal the observation
    assert abs(update["m_post"] - z_obs) < 1e-4
    # Posterior variance must equal observation variance
    assert abs(update["p_post"] - v_obs) < 1e-4

    # With tau^2 -> infinity (very large between-district variance),
    # partial pooling shrinkage lambda is 0, so data_share omega is 1.0
    m_pooled, p_pooled, shrink_lambda, omega = kf.apply_partial_pooling(
        district_m=update["m_post"],
        district_p=update["p_post"],
        state_m=2.0,
        tau2=1e8,  # tau -> infinity
    )
    assert abs(m_pooled - z_obs) < 1e-4
    assert abs(omega - 1.0) < 1e-4


def test_section_5_property_b_identical_sources_variance():
    """
    (b) With n identical independent sources each with variance v,
    the information is sum(1/v) = n/v, so the posterior variance falls as v/n (1/n scaling).
    """
    kf = KalmanFusion()
    m_prior = 3.0
    p_prior = 1e6  # Diffuse prior

    v_single = 0.60
    z_val = 3.50

    # 1 source
    up_1 = kf.update(
        m_prior, p_prior,
        [{"source_id": "s1", "z": z_val, "v": v_single, "gate_pass": True}],
    )
    var_1 = up_1["p_post"]

    # 4 identical sources
    up_4 = kf.update(
        m_prior, p_prior,
        [{"source_id": f"s{i}", "z": z_val, "v": v_single, "gate_pass": True} for i in range(4)],
    )
    var_4 = up_4["p_post"]

    # Ratio should be exactly 1/4
    expected_ratio = 1.0 / 4.0
    actual_ratio = var_4 / var_1
    assert abs(actual_ratio - expected_ratio) < 1e-3


def test_section_5_property_c_attribution_sum():
    """
    (c) Contributions plus prior share sum to the total change.
    m_post - m_prior = sum_k contribution_k
    where contribution_k = w_k * (z_k - m_prior).
    """
    kf = KalmanFusion()
    m_prior = 3.20
    p_prior = 0.25

    observations = [
        {"source_id": "ncs", "z": 4.10, "v": 0.15, "gate_pass": True},
        {"source_id": "portal", "z": 2.80, "v": 0.10, "gate_pass": True},
        {"source_id": "eshram", "z": 3.50, "v": 0.20, "gate_pass": True},
    ]

    update = kf.update(m_prior, p_prior, observations)

    total_change = update["m_post"] - m_prior
    sum_contributions = sum(c["contribution"] for c in update["contributions"])

    # Sum of source contributions must equal total update change
    assert abs(total_change - sum_contributions) < 1e-5

    # Sum of all weights (prior weight + source weights) must equal 1.0
    sum_weights = update["prior_weight"] + sum(c["weight"] for c in update["contributions"])
    assert abs(sum_weights - 1.0) < 1e-5


def test_section_5_property_d_noisy_source_downweighted():
    """
    (d) A source made artificially noisy gets its r_k reduced and its weight cut.
    """
    gate = ReliabilityGate()
    v_bar = 0.10

    # 1. Clean history (low excess deviation)
    clean_devs = [0.05, 0.08, -0.04, 0.06, -0.05, 0.07]
    r_k_clean = gate.calculate_r_k(v_bar, clean_devs)

    # 2. Artificially noisy history (large leave-one-out deviations)
    noisy_devs = [0.85, -1.20, 0.95, -1.40, 1.10, -1.05]
    r_k_noisy = gate.calculate_r_k(v_bar, noisy_devs)

    # Reliability factor r_k must be significantly reduced
    assert r_k_noisy < r_k_clean
    assert r_k_noisy < 0.20

    # Test weight in Kalman update: higher noise -> higher v -> lower weight
    kf = KalmanFusion()
    builder = EvidenceUnitBuilder()

    ev_clean = builder.build_evidence(n_eff=20, r_k=r_k_clean)
    ev_noisy = builder.build_evidence(n_eff=20, r_k=r_k_noisy)

    # Observation variance v is inversely proportional to r_k
    assert ev_noisy["v"] > ev_clean["v"]

    update = kf.update(
        m_prior=3.0, p_prior=0.5,
        observations=[
            {"source_id": "clean_src", "z": 3.5, "v": ev_clean["v"], "gate_pass": True},
            {"source_id": "noisy_src", "z": 3.5, "v": ev_noisy["v"], "gate_pass": True},
        ]
    )

    w_clean = next(c["weight"] for c in update["contributions"] if c["source_id"] == "clean_src")
    w_noisy = next(c["weight"] for c in update["contributions"] if c["source_id"] == "noisy_src")

    # Weight of noisy source must be cut significantly
    assert w_noisy < w_clean / 2.0


def test_section_5_property_e_stale_source_gated_out():
    """
    (e) A stale source (age > 2 * nominal_update_days) is gated out and contributes nothing.
    """
    gate = ReliabilityGate(max_age_multiplier=2.0)
    nominal_days = 30

    # Fresh source (15 days old)
    fresh_pass, fresh_reason = gate.evaluate_gate(
        n_eff_trailing_90d=50, age_days=15, nominal_update_days=nominal_days
    )
    assert fresh_pass is True
    assert fresh_reason is None

    # Stale source (75 days old > 2 * 30 = 60 days)
    stale_pass, stale_reason = gate.evaluate_gate(
        n_eff_trailing_90d=50, age_days=75, nominal_update_days=nominal_days
    )
    assert stale_pass is False
    assert "Stale" in stale_reason

    # In Kalman update, gated out source has weight = 0 and contribution = 0
    kf = KalmanFusion()
    update = kf.update(
        m_prior=3.0, p_prior=0.5,
        observations=[
            {"source_id": "fresh", "z": 4.0, "v": 0.1, "gate_pass": True},
            {"source_id": "stale", "z": 5.0, "v": 0.1, "gate_pass": False, "gate_reason": stale_reason},
        ]
    )

    stale_contrib = next(c for c in update["contributions"] if c["source_id"] == "stale")
    assert stale_contrib["weight"] == 0.0
    assert stale_contrib["contribution"] == 0.0
    assert stale_contrib["gate_pass"] is False


@pytest.mark.asyncio
async def test_demand_index_api_queryability():
    """
    Verifies that a cell's LDI, credible interval, confidence badge,
    and source contributions are queryable via the API.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Query demand index (Karnataka, Automotive, EV Service Technician)
        res = await client.get("/api/v1/demand-index?state=KA&trade=EV Service Technician")
        assert res.status_code == 200
        items = res.json()
        assert len(items) > 0

        ev_item = items[0]
        assert ev_item["state_code"] == "KA"
        assert "EV Service Technician" in ev_item["trade_name"]
        assert 0 <= ev_item["ldi"] <= 100
        assert ev_item["ldi_lo"] <= ev_item["ldi_hi"]
        assert ev_item["confidence"] in ["High", "Medium", "Low"]
        assert ev_item["data_mode"] == "synthetic"
        assert "V" in ev_item["descriptors"]
        assert "G" in ev_item["descriptors"]

        # 2. Query Explain / Attribution for this cell
        dist_id = 1
        trade_id = ev_item["trade_id"]
        explain_res = await client.get(f"/api/v1/explain?district_id={dist_id}&trade_id={trade_id}")
        assert explain_res.status_code == 200
        explain_data = explain_res.json()

        assert "source_contributions" in explain_data
        assert len(explain_data["source_contributions"]) > 0
        assert explain_data["cell"]["district_id"] == dist_id
        assert explain_data["cell"]["trade_id"] == trade_id
        assert "narrative" in explain_data
