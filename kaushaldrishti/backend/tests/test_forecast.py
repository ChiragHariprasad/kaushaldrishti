"""
Unit and Integration Tests for Forecasting Pipeline (Layer 6).
Covers Baselines, State-Space, LightGBM, Conformal Calibration, Ensemble,
Hierarchical Reconciliation, and Forecast/Validation APIs.
"""

import numpy as np
import pandas as pd
import pytest
from httpx import AsyncClient

from pipelines.forecast.baselines import SeasonalNaiveForecaster, SimpleETSForecaster
from pipelines.forecast.conformal import ConformalCalibrator
from pipelines.forecast.ensemble import EnsembleDemandForecaster, pinball_loss
from pipelines.forecast.lightgbm_model import GlobalLightGBMForecaster
from pipelines.forecast.reconciliation import HierarchicalReconciler
from pipelines.forecast.state_space import StateSpaceForecaster


# ─── 1. Baselines ────────────────────────────────────────────────────────────


def test_seasonal_naive_forecaster():
    """Verify seasonal naive repeats lag-12 with expanding uncertainty."""
    sn = SeasonalNaiveForecaster(season_length=12)
    # 24 months of synthetic seasonal data: pattern [10, 20, 30, ... 120] repeated twice
    history = [float((i % 12 + 1) * 10) for i in range(24)]
    preds, stds = sn.forecast(history, horizon=6)

    assert len(preds) == 6
    assert len(stds) == 6
    # For h=1, matches history[-12] == 10.0
    assert preds[0] == 10.0
    assert preds[1] == 20.0
    # Uncertainty increases or remains positive
    assert all(s > 0 for s in stds)


def test_ets_forecaster():
    """Verify SimpleETS generates valid trend + seasonal forecasts."""
    ets = SimpleETSForecaster()
    history = [100.0 + 2.0 * i + 10.0 * np.sin(2 * np.pi * i / 12) for i in range(36)]
    preds, stds = ets.forecast(history, horizon=12)

    assert len(preds) == 12
    assert len(stds) == 12
    # Upward trend is projected
    assert preds[-1] > preds[0]
    assert all(s > 0 for s in stds)


# ─── 2. State-Space Forecaster ──────────────────────────────────────────────


def test_state_space_projection_mechanics():
    """Verify Kalman state projection, monotone variance growth, and quantile ordering."""
    ss = StateSpaceForecaster(phi=0.95, q_theta=0.04)
    m_t = 4.5
    b_t = 0.05
    p_t = 0.02
    res = ss.project_cell(m_t, b_t, p_t, horizon=12)

    means = res["mean"]
    sigmas = res["sigma"]
    q10 = res["q10"]
    q90 = res["q90"]
    q025 = res["q025"]
    q975 = res["q975"]

    # 1. Monotone variance growth
    for h in range(len(sigmas) - 1):
        assert sigmas[h + 1] > sigmas[h]

    # 2. Quantile ordering: q025 < q10 < mean < q90 < q975
    for h in range(12):
        assert q025[h] < q10[h]
        assert q10[h] < q90[h]
        assert q90[h] < q975[h]
        assert q10[h] <= means[h] <= q90[h]

    # 3. Damped trend: cumulative drift < h * b_t
    undamped_12 = 12 * b_t
    actual_drift_12 = res["log_mean"][11] - m_t
    assert actual_drift_12 < undamped_12


# ─── 3. LightGBM Forecaster ─────────────────────────────────────────────────


def test_lightgbm_features_and_prediction():
    """Verify LightGBM feature matrix generation and multi-horizon predictions."""
    # Synthetic mini-panel (2 districts x 2 trades x 24 months)
    records = []
    for d in [1, 2]:
        for tr in [1, 2]:
            for m_idx in range(24):
                month_str = f"2023-{m_idx + 1:02d}" if m_idx < 12 else f"2024-{m_idx - 11:02d}"
                records.append({
                    "month": month_str,
                    "district_id": d,
                    "trade_id": tr,
                    "V": 50.0 + 5.0 * m_idx + np.random.uniform(0, 5),
                    "m": 4.0,
                    "slope": 0.02,
                    "P": 0.03,
                    "B": 1.2,
                    "R": 1.0,
                    "I": 0.5,
                    "P_persist": 2,
                    "data_mode": "synthetic",
                })
    panel_df = pd.DataFrame(records)

    lgbm = GlobalLightGBMForecaster(horizons=[3, 6])
    features_df = lgbm.prepare_features(panel_df)
    assert not features_df.empty
    assert "lag_1" in features_df.columns
    assert "roll_mean_6" in features_df.columns
    assert "sin_month" in features_df.columns

    lgbm.fit(features_df)
    latest = features_df[features_df["month"] == "2024-12"].head(4)
    preds, sigmas, q10, q90 = lgbm.predict(latest, horizon=3)

    assert len(preds) == len(latest)
    assert all(p >= 0 for p in preds)
    assert all(q10[i] <= preds[i] <= q90[i] for i in range(len(preds)))


# ─── 4. Split-Conformal Calibration ─────────────────────────────────────────


def test_conformal_calibrator():
    """Verify split-conformal multiplier derivation and effective sigma_h."""
    calibrator = ConformalCalibrator(target_coverages=[0.80, 0.95])
    np.random.seed(42)
    n = 200
    y_true = np.random.normal(100, 15, size=n)
    y_pred = y_true + np.random.normal(0, 10, size=n)
    sigma_est = np.full(n, 10.0)

    calibrator.calibrate(y_true, y_pred, sigma_est)
    assert calibrator.calibrated
    assert 0.80 in calibrator.q_multipliers
    assert 0.95 in calibrator.q_multipliers
    # 95% multiplier should be strictly greater than 80% multiplier
    assert calibrator.q_multipliers[0.95] > calibrator.q_multipliers[0.80]

    intervals = calibrator.predict_intervals(y_pred, sigma_est)
    # Check effective sigma_h equation from Section 6: (q90 - q10) / (2 * 1.2816)
    expected_sigma_h = (intervals["q90"] - intervals["q10"]) / (2.0 * 1.2816)
    np.testing.assert_allclose(intervals["sigma_h"], expected_sigma_h, rtol=1e-5)

    # Check empirical coverage on training residuals
    cov_stats = calibrator.evaluate_coverage(y_true, intervals)
    assert cov_stats["coverage_80"] >= 0.75
    assert cov_stats["coverage_95"] >= 0.90


# ─── 5. Ensemble Forecaster ─────────────────────────────────────────────────


def test_ensemble_weighting_and_cohort_horizon():
    """Verify convex ensemble combination and cohort-aligned horizon."""
    ens = EnsembleDemandForecaster(horizons=[3, 6, 12])
    
    # Verify pinball loss weighting produces valid convex weights
    losses = {
        3: {"state_space": 10.0, "lightgbm": 8.0, "ets": 12.0, "seasonal_naive": 15.0},
        6: {"state_space": 12.0, "lightgbm": 10.0, "ets": 14.0, "seasonal_naive": 16.0},
        12: {"state_space": 15.0, "lightgbm": 13.0, "ets": 17.0, "seasonal_naive": 19.0},
    }
    weights = ens.compute_weights_from_losses(losses)
    for h in [3, 6, 12]:
        w_sum = sum(weights[h].values())
        assert pytest.approx(w_sum, abs=1e-5) == 1.0
        # Best model (lightgbm) gets highest weight
        assert weights[h]["lightgbm"] > weights[h]["seasonal_naive"]

    # Test single-cell forecast for standard horizon h=6
    history = [float(50 + 2 * i) for i in range(24)]
    res_6 = ens.predict_cell(
        history_openings=history,
        m_t=4.5,
        b_t=0.03,
        p_t=0.02,
        horizon=6,
        lgbm_pred_openings=95.0,
        lgbm_sigma=10.0,
    )
    assert res_6["q10"] <= res_6["mean"] <= res_6["q90"]
    assert res_6["sigma_h"] > 0

    # Test cohort-aligned horizon (e.g. L=4 months)
    res_cohort = ens.predict_cell(
        history_openings=history,
        m_t=4.5,
        b_t=0.03,
        p_t=0.02,
        horizon=4,
    )
    assert res_cohort["mean"] > 0
    assert res_cohort["q10"] <= res_cohort["mean"] <= res_cohort["q90"]


# ─── 6. Hierarchical Reconciliation ─────────────────────────────────────────


def test_hierarchical_reconciliation():
    """Verify bottom-up reconciliation preserves state and national totals."""
    reconciler = HierarchicalReconciler(method="bottom_up")
    district_forecasts = {1: 100.0, 2: 150.0, 3: 200.0, 4: 80.0}
    district_to_state = {1: "KA", 2: "KA", 3: "TN", 4: "UP"}

    reconciled = reconciler.reconcile_bottom_up(district_forecasts, district_to_state)

    # KA = 100 + 150 = 250
    assert reconciled["state"]["KA"] == 250.0
    # TN = 200
    assert reconciled["state"]["TN"] == 200.0
    # UP = 80
    assert reconciled["state"]["UP"] == 80.0
    # National = 250 + 200 + 80 = 530
    assert reconciled["national"]["total"] == 530.0


# ─── 7. API Endpoints ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_forecast_and_validation_api(client: AsyncClient):
    """Verify GET /api/v1/forecasts and GET /api/v1/validation."""
    # 1. Forecasts endpoint
    fc_resp = await client.get("/api/v1/forecasts?limit=10")
    assert fc_resp.status_code == 200
    data = fc_resp.json()
    assert "items" in data
    assert "total" in data

    if data["items"]:
        item = data["items"][0]
        assert "mean" in item
        assert "q10" in item
        assert "q90" in item
        assert "horizon" in item
        assert "data_mode" in item
        assert item["q10"] <= item["mean"] <= item["q90"]

    # 2. Validation endpoint
    val_resp = await client.get("/api/v1/validation")
    assert val_resp.status_code == 200
    val_data = val_resp.json()
    assert "horizons" in val_data
    assert "metrics" in val_data
    assert "target_coverage_80" in val_data
    assert "3" in val_data["metrics"] or 3 in val_data["metrics"]
