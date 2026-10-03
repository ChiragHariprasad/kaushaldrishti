"""
Split-Conformal Calibration (Layer 6).
Provides distribution-free, finite-sample calibrated prediction intervals
scaled by local volatility, targeting 80% and 95% empirical coverage.
"""

from typing import Dict, List, Optional, Tuple, Union
import numpy as np


class ConformalCalibrator:
    """
    Split-Conformal Prediction Interval Calibrator.
    
    Calibration rule:
      s_i = |y_i - y_hat_i| / max(sigma_i, 1e-4)
      q_{1-alpha} = Quantile_{ceil((n+1)(1-alpha))/n}(s)
      Interval: [y_hat - q_{1-alpha} * sigma, y_hat + q_{1-alpha} * sigma]
      Effective sigma_h: (q90 - q10) / (2 * 1.2816)
    """

    def __init__(self, target_coverages: List[float] = [0.80, 0.95]):
        self.target_coverages = target_coverages
        self.q_multipliers: Dict[float, float] = {0.80: 1.2816, 0.95: 1.96}
        self.calibrated = False

    def calibrate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        sigma_est: np.ndarray,
    ) -> "ConformalCalibrator":
        """
        Calibrate quantile multipliers using a holdout calibration set.
        """
        y_true = np.asarray(y_true, dtype=float)
        y_pred = np.asarray(y_pred, dtype=float)
        sigma_est = np.asarray(sigma_est, dtype=float)

        # Nonconformity scores scaled by local volatility
        residuals = np.abs(y_true - y_pred)
        safe_sigma = np.maximum(sigma_est, 1e-4)
        scores = residuals / safe_sigma

        n = len(scores)
        if n < 5:
            # Insufficient samples: fall back to Gaussian multipliers
            self.q_multipliers = {0.80: 1.2816, 0.95: 1.96}
            self.calibrated = True
            return self

        # Finite-sample adjusted quantile
        for cov in self.target_coverages:
            rank = int(np.ceil((n + 1) * cov))
            p_val = min(1.0, rank / n)
            q_val = float(np.quantile(scores, p_val, method="higher"))
            self.q_multipliers[cov] = max(0.5, q_val)

        self.calibrated = True
        return self

    def predict_intervals(
        self,
        y_pred: np.ndarray,
        sigma_est: np.ndarray,
    ) -> Dict[str, np.ndarray]:
        """
        Generate calibrated prediction intervals and effective sampling sigma.
        Returns dict with:
          'q10': 10th percentile
          'q90': 90th percentile
          'q025': 2.5th percentile
          'q975': 97.5th percentile
          'sigma_h': effective standard error (q90 - q10)/(2*1.2816)
        """
        y_pred = np.asarray(y_pred, dtype=float)
        sigma_est = np.asarray(sigma_est, dtype=float)

        q80_mult = self.q_multipliers.get(0.80, 1.2816)
        q95_mult = self.q_multipliers.get(0.95, 1.96)

        margin_80 = q80_mult * sigma_est
        margin_95 = q95_mult * sigma_est

        q10 = np.maximum(0.0, y_pred - margin_80)
        q90 = np.maximum(0.0, y_pred + margin_80)
        q025 = np.maximum(0.0, y_pred - margin_95)
        q975 = np.maximum(0.0, y_pred + margin_95)

        # Master prompt formula: sigma_h = (q90 - q10) / (2 * 1.2816)
        sigma_h = (q90 - q10) / (2.0 * 1.2816)

        return {
            "q10": q10,
            "q90": q90,
            "q025": q025,
            "q975": q975,
            "sigma_h": sigma_h,
        }

    def evaluate_coverage(
        self,
        y_true: np.ndarray,
        intervals: Dict[str, np.ndarray],
    ) -> Dict[str, float]:
        """
        Compute empirical coverage and interval width.
        """
        y_true = np.asarray(y_true, dtype=float)
        q10 = intervals["q10"]
        q90 = intervals["q90"]
        q025 = intervals["q025"]
        q975 = intervals["q975"]

        cov_80 = float(np.mean((y_true >= q10) & (y_true <= q90)))
        cov_95 = float(np.mean((y_true >= q025) & (y_true <= q975)))
        mean_width_80 = float(np.mean(q90 - q10))

        return {
            "coverage_80": cov_80,
            "coverage_95": cov_95,
            "mean_width_80": mean_width_80,
        }
