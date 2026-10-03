"""
Section 8 Tests: Probabilistic Gap, Early Warning Alerts & Multilingual Explainability.
Tests:
  1. Tolerance calculation tau = max(0.10 * E[D], 5.0).
  2. Probabilities sum to 1.0 and severity is bounded [0, 100].
  3. Section 8 worked example: E[D]=198, E[S]=162, tau=20, sigma_G=38 -> p_S ~ 0.66, severity ~ 40.
  4. Hysteresis state machine (persistence, no flicker, de-escalation margin).
  5. Mutual exclusivity (Shortage vs Saturation).
  6. Multilingual explainability in 4 languages (en, hi, kn, ta).
  7. API Endpoints queryability (/gaps, /alerts, /rankings, /explain-gap).
"""

import pytest
from httpx import AsyncClient

from pipelines.gap.engine import GapEngine
from pipelines.gap.explain import MultilingualExplainer
from pipelines.gap.flags import CellSignalInput, HysteresisAlertManager


# ─── 1. Mathematical Formulas ───────────────────────────────────────────────


def test_tolerance_calculation():
    """Verify tau = max(0.10 * E[D], 5.0)."""
    engine = GapEngine()
    # Small demand: bounded by 5.0
    assert engine.compute_tolerance(20.0) == 5.0
    assert engine.compute_tolerance(50.0) == 5.0
    # Larger demand: 10% of demand
    assert engine.compute_tolerance(100.0) == 10.0
    assert engine.compute_tolerance(198.0) == 19.8


def test_probability_normalization_and_severity_bounds():
    """Verify probabilities sum to 1.0 and severity is strictly within [0, 100]."""
    engine = GapEngine()
    for d, s in [(150, 100), (100, 150), (200, 200), (500, 20)]:
        res = engine.compute_cell_gap(d_mean=d, d_sigma=20.0, s_mean=s, s_sigma=15.0)
        p_total = res["p_shortage"] + res["p_oversupply"] + res["p_balanced"]
        assert pytest.approx(p_total, abs=1e-3) == 1.0
        assert 0.0 <= res["severity"] <= 100.0


def test_section_8_worked_example():
    """
    Section 8 Worked Example:
    E[D]=198, E[S]=162, tau=20, sigma_G=38 gives p_S ~ 0.66, severity ~ 40, Emerging Shortage on 2nd refresh.
    """
    engine = GapEngine()
    # With d_mean=198, s_mean=162, sigma_G=38 (e.g. d_sigma=26.87, s_sigma=26.87)
    sigma_part = 38.0 / (2.0**0.5)
    res = engine.compute_cell_gap(d_mean=198.0, d_sigma=sigma_part, s_mean=162.0, s_sigma=sigma_part)

    # 1. Expected gap: 198 - 162 = 36
    assert abs(res["g_mean"] - 36.0) < 0.1

    # 2. Probability of shortage p_S ~ 0.66
    assert pytest.approx(res["p_shortage"], abs=0.03) == 0.66

    # 3. Severity ~ 40
    assert pytest.approx(res["severity"], abs=2.5) == 40.0

    # 4. Status: Shortage
    assert res["status"] == "Shortage"

    # 5. Hysteresis manager: Emerging Shortage candidate confirmed on second refresh
    mgr = HysteresisAlertManager()
    sig = CellSignalInput(
        p_shortage=res["p_shortage"],
        p_oversupply=res["p_oversupply"],
        gap_rate=res["gap_rate"],
        expected_gap=res["g_mean"],
        demand_trend=0.15,
        capacity_trend=0.05,
        confidence="Medium",
        interval_spread=0.45,
        corroboration_i=1.5,
    )

    # Refresh 1: Candidate evaluated as Emerging Shortage, held in Stable (count 1)
    flag_1, count_1, _, reason_1 = mgr.step(current_flag="Stable", persistence_count=0, sig=sig)
    assert flag_1 == "Stable"

    # Refresh 2: Condition persists -> confirms Emerging Shortage
    flag_2, count_2, _, reason_2 = mgr.step(current_flag="Stable", persistence_count=1, sig=sig)
    assert flag_2 == "Emerging Shortage"
    assert "persisted for 2 consecutive refreshes" in reason_2


# ─── 2. Hysteresis State Machine ───────────────────────────────────────────


def test_hysteresis_anti_flicker_and_de_escalation():
    """Verify state machine requires 2 refreshes to clear and respects de-escalation margin."""
    mgr = HysteresisAlertManager(de_escalate_margin=0.10)

    # Currently in Acute Shortage (threshold 0.80)
    sig_acute = CellSignalInput(
        p_shortage=0.85,
        p_oversupply=0.01,
        gap_rate=0.25,
        expected_gap=50.0,
        demand_trend=0.20,
        capacity_trend=0.05,
        confidence="High",
        interval_spread=0.3,
        corroboration_i=2.0,
    )
    flag, count, _, _ = mgr.step("Acute Shortage", persistence_count=2, sig=sig_acute)
    assert flag == "Acute Shortage"

    # Transient dip to p_shortage = 0.75 (above 0.70 de-escalate margin): remains Acute Shortage
    sig_dip = CellSignalInput(
        p_shortage=0.75,
        p_oversupply=0.05,
        gap_rate=0.18,
        expected_gap=35.0,
        demand_trend=0.10,
        capacity_trend=0.05,
        confidence="High",
        interval_spread=0.3,
        corroboration_i=2.0,
    )
    flag_dip, _, _, _ = mgr.step("Acute Shortage", persistence_count=0, sig=sig_dip)
    assert flag_dip == "Acute Shortage"

    # Drops below 0.70 (e.g. 0.45) for 1 refresh: retains current state, marks progress
    sig_clear = CellSignalInput(
        p_shortage=0.45,
        p_oversupply=0.10,
        gap_rate=0.05,
        expected_gap=10.0,
        demand_trend=0.02,
        capacity_trend=0.02,
        confidence="High",
        interval_spread=0.3,
        corroboration_i=2.0,
    )
    flag_c1, count_1, _, _ = mgr.step("Acute Shortage", persistence_count=0, sig=sig_clear)
    # First refresh: maintains Acute Shortage (count becomes 1)
    assert flag_c1 == "Acute Shortage"

    # Second refresh below threshold: de-escalates to Stable
    flag_c2, count_2, _, reason = mgr.step("Acute Shortage", persistence_count=count_1, sig=sig_clear)
    assert flag_c2 == "Stable"
    assert "fell below de-escalation margin" in reason


def test_mutual_exclusivity():
    """Verify shortage and saturation are mutually exclusive."""
    mgr = HysteresisAlertManager()
    sig_short = CellSignalInput(
        p_shortage=0.85,
        p_oversupply=0.02,
        gap_rate=0.30,
        expected_gap=60.0,
        demand_trend=0.20,
        capacity_trend=0.05,
        confidence="High",
        interval_spread=0.3,
        corroboration_i=2.0,
    )
    cand_short, _ = mgr.evaluate_candidate_flag(sig_short)
    assert cand_short == "Acute Shortage"
    assert "Saturation" not in cand_short

    sig_sat = CellSignalInput(
        p_shortage=0.01,
        p_oversupply=0.85,
        gap_rate=-0.30,
        expected_gap=-60.0,
        demand_trend=-0.10,
        capacity_trend=0.15,
        confidence="High",
        interval_spread=0.3,
        corroboration_i=2.0,
    )
    cand_sat, _ = mgr.evaluate_candidate_flag(sig_sat)
    assert cand_sat == "Saturated"
    assert "Shortage" not in cand_sat


# ─── 3. Multilingual Explainability ─────────────────────────────────────────


def test_multilingual_explainer_all_languages():
    """Verify deterministic explanation generation in en, hi, kn, ta."""
    explainer = MultilingualExplainer()
    gap_info = {
        "d_mean": 250.0,
        "s_mean": 180.0,
        "g_mean": 70.0,
        "p_shortage": 0.88,
        "p_oversupply": 0.01,
        "severity": 75.0,
    }

    for lang in ["en", "hi", "kn", "ta"]:
        res = explainer.explain_cell(
            trade_name="EV Service Technician",
            district_name="Bengaluru Urban",
            state_code="KA",
            flag="Acute Shortage",
            overlays=["Rapid Growth"],
            gap_info=gap_info,
            confidence="High",
            data_mode="synthetic",
            lang=lang,
        )
        assert res["lang"] == lang
        assert res["narrative"]
        assert len(res["narrative"]) > 20
        assert res["suggested_action"]
        assert res["severity"] == 75.0

    # Verify specific Indic terms
    hi_res = explainer.explain_cell("EV Technician", "Bengaluru", "KA", "Acute Shortage", [], gap_info, lang="hi")
    assert "गंभीर कमी" in hi_res["flag_label"] or "कमी" in hi_res["narrative"]

    kn_res = explainer.explain_cell("EV Technician", "Bengaluru", "KA", "Acute Shortage", [], gap_info, lang="kn")
    assert "ತೀವ್ರ ಕೊರತೆ" in kn_res["flag_label"] or "ಕೊರತೆ" in kn_res["narrative"]


# ─── 4. API Endpoints ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_gap_and_alert_api(client: AsyncClient):
    """Verify /gaps, /alerts, /rankings, /explain-gap endpoints."""
    # 1. Gaps
    g_res = await client.get("/api/v1/gaps?district_id=1&window_months=12")
    assert g_res.status_code == 200
    g_data = g_res.json()
    assert "items" in g_data
    assert len(g_data["items"]) > 0
    item = g_data["items"][0]
    assert "severity" in item
    assert "p_shortage" in item
    assert item["status"] in ["Shortage", "Balanced", "Surplus"]
    assert item["data_mode"] == "synthetic"

    # 2. Alerts
    a_res = await client.get("/api/v1/alerts?limit=10")
    assert a_res.status_code == 200
    a_data = a_res.json()
    assert "items" in a_data
    if a_data["items"]:
        alert = a_data["items"][0]
        assert "flag" in alert
        assert "persistence_count" in alert
        assert "suggested_action" in alert

    # 3. Rankings
    r_res = await client.get("/api/v1/rankings?limit=5")
    assert r_res.status_code == 200
    r_data = r_res.json()
    assert "top_shortages" in r_data
    assert "top_saturations" in r_data
    if r_data["top_shortages"]:
        assert r_data["top_shortages"][0]["status"] == "Shortage"

    # 4. Explain Gap
    ex_res = await client.get("/api/v1/explain-gap?district_id=1&trade_id=1&lang=hi")
    assert ex_res.status_code == 200
    ex_data = ex_res.json()
    assert ex_data["lang"] == "hi"
    assert "narrative" in ex_data
    assert "suggested_action" in ex_data
