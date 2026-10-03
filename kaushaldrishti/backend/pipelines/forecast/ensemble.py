"""
Ensemble Demand Forecaster (Layer 6).
Combines State-Space, LightGBM, ETS, and Seasonal Naive forecasts using
rolling-origin CV weights that minimise pinball loss.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd

from pipelines.forecast.baselines import SeasonalNaiveForecaster, SimpleETSForecaster
from pipelines.forecast.conformal import ConformalCalibrator
from pipelines.forecast.state_space import StateSpaceForecaster


def pinball_loss(y_true: np.ndarray, y_pred: np.ndarray, tau: float) -> float:
    """
    Computes asymmetric quantile pinball loss:
      L_tau(y, q) = max(tau * (y - q), (tau - 1) * (y - q))
    """
    diff = y_true - y_pred
    return float(np.mean(np.maximum(tau * diff, (tau - 1.0) * diff)))


def multi_quantile_loss(
    y_true: np.ndarray,
    point_pred: np.ndarray,
    q10_pred: np.ndarray,
    q90_pred: np.ndarray,
) -> float:
    """
    Composite pinball loss across median (tau=0.5) and 80% bounds (tau=0.1, 0.9).
    """
    l10 = pinball_loss(y_true, q10_pred, 0.10)
    l50 = pinball_loss(y_true, point_pred, 0.50)
    l90 = pinball_loss(y_true, q90_pred, 0.90)
    return l10 + 2.0 * l50 + l90


class EnsembleDemandForecaster:
    """
    Ensemble forecaster combining:
      1. StateSpace (Bayesian Kalman projection)
      2. LightGBM (Global panel gradient boosting)
      3. ETS (Holt-Winters level + trend + season)
      4. Seasonal Naive (Lag-12 benchmark)
    """

    def __init__(
        self,
        horizons: List[int] = [3, 6, 12],
        model_names: Optional[List[str]] = None,
    ):
        self.horizons = horizons
        self.model_names = model_names or ["state_space", "lightgbm", "ets", "seasonal_naive"]
        # Default balanced weights: 0.40 LightGBM, 0.35 StateSpace, 0.15 ETS, 0.10 Naive
        self.weights: Dict[int, Dict[str, float]] = {
            h: {"lightgbm": 0.40, "state_space": 0.35, "ets": 0.15, "seasonal_naive": 0.10}
            for h in self.horizons
        }
        self.calibrators: Dict[int, ConformalCalibrator] = {
            h: ConformalCalibrator() for h in self.horizons
        }

    def compute_weights_from_losses(
        self,
        horizon_model_losses: Dict[int, Dict[str, float]],
        temperature: float = 0.5,
    ) -> Dict[int, Dict[str, float]]:
        """
        Computes convex ensemble weights inversely proportional to pinball loss:
          w_m(h) propto exp(- (loss_m - min_loss) / temperature)
        """
        updated_weights = {}
        for h, model_losses in horizon_model_losses.items():
            losses = np.array([model_losses.get(m, 1.0) for m in self.model_names])
            min_loss = np.min(losses)
            # Softmax with temperature
            exp_neg = np.exp(-(losses - min_loss) / max(1e-3, temperature))
            w = exp_neg / np.sum(exp_neg)
            updated_weights[h] = {m: float(w[i]) for i, m in enumerate(self.model_names)}

        self.weights = updated_weights
        return self.weights

    def predict_cell(
        self,
        history_openings: List[float],
        m_t: float,
        b_t: float,
        p_t: float,
        horizon: int,
        lgbm_pred_openings: Optional[float] = None,
        lgbm_sigma: Optional[float] = None,
    ) -> Dict[str, float]:
        """
        Produce ensemble forecast for a single cell at a given horizon.
        Handles standard horizons (3, 6, 12) or custom cohort-aligned horizon (e.g. L=4, 6, 12).
        """
        # Determine weight vector for horizon (fallback to nearest if custom horizon L)
        if horizon in self.weights:
            w_dict = self.weights[horizon]
        else:
            closest_h = min(self.weights.keys(), key=lambda k: abs(k - horizon))
            w_dict = self.weights[closest_h]

        preds: Dict[str, float] = {}
        sigmas: Dict[str, float] = {}

        # 1. State-Space
        ss = StateSpaceForecaster()
        ss_mean, ss_q10, ss_q90 = ss.forecast_horizon(m_t, b_t, p_t, horizon)
        preds["state_space"] = ss_mean
        sigmas["state_space"] = max(1e-3, (ss_q90 - ss_q10) / (2.0 * 1.2816))

        # 2. LightGBM
        if lgbm_pred_openings is not None:
            preds["lightgbm"] = float(lgbm_pred_openings)
            sigmas["lightgbm"] = float(lgbm_sigma or 0.25 * lgbm_pred_openings)
        else:
            # If LGBM not supplied for this single cell, fall back to state space
            preds["lightgbm"] = ss_mean
            sigmas["lightgbm"] = sigmas["state_space"]

        # 3. ETS
        ets = SimpleETSForecaster()
        ets_preds, ets_stds = ets.forecast(history_openings, horizon)
        preds["ets"] = float(ets_preds[horizon - 1])
        sigmas["ets"] = float(ets_stds[horizon - 1])

        # 4. Seasonal Naive
        sn = SeasonalNaiveForecaster()
        sn_preds, sn_stds = sn.forecast(history_openings, horizon)
        preds["seasonal_naive"] = float(sn_preds[horizon - 1])
        sigmas["seasonal_naive"] = float(sn_stds[horizon - 1])

        # Combine predictions using convex weights
        ens_mean = sum(w_dict.get(m, 0.0) * max(0.0, preds[m]) for m in self.model_names)

        # Combine variances: law of total variance (within-model + between-model)
        within_var = sum(w_dict.get(m, 0.0) * (sigmas[m] ** 2) for m in self.model_names)
        between_var = sum(
            w_dict.get(m, 0.0) * ((preds[m] - ens_mean) ** 2) for m in self.model_names
        )
        total_sigma = np.sqrt(max(1e-4, within_var + between_var))

        # Apply conformal calibration if available for this horizon
        calibrator = self.calibrators.get(horizon) or self.calibrators.get(
            min(self.calibrators.keys(), key=lambda k: abs(k - horizon))
        )
        if calibrator and calibrator.calibrated:
            int_res = calibrator.predict_intervals(np.array([ens_mean]), np.array([total_sigma]))
            q10 = float(int_res["q10"][0])
            q90 = float(int_res["q90"][0])
            sigma_h = float(int_res["sigma_h"][0])
        else:
            # Standard Gaussian margin with cohort horizon scale sqrt(L/12)
            margin = 1.2816 * total_sigma * np.sqrt(max(1.0, horizon / 12.0))
            q10 = max(0.0, ens_mean - margin)
            q90 = ens_mean + margin
            sigma_h = (q90 - q10) / (2.0 * 1.2816)

        return {
            "mean": float(ens_mean),
            "q10": float(q10),
            "q90": float(q90),
            "sigma_h": float(sigma_h),
            "model_preds": preds,
            "weights": w_dict,
        }
