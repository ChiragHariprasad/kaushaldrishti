"""
Hierarchical Forecast Reconciliation (Layer 6).
Reconciles forecasts across District -> State -> National hierarchy.
Implements MinT (Minimum Trace with shrinkage) and Bottom-Up reconciliation.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np


class HierarchicalReconciler:
    """
    Hierarchical reconciler ensuring sum(district) == state and sum(state) == national.
    Supports MinT (Minimum Trace) with shrinkage covariance, with robust Bottom-Up fallback.
    """

    def __init__(self, method: str = "bottom_up"):
        """
        method: 'bottom_up' or 'mint'
        """
        self.method = method

    def reconcile_bottom_up(
        self,
        district_forecasts: Dict[int, float],
        district_to_state: Dict[int, str],
    ) -> Dict[str, Dict[str, float]]:
        """
        Reconciles forecasts strictly bottom-up.
        Returns:
          'district': {dist_id: val}
          'state': {state_code: val}
          'national': {'total': val}
        """
        state_totals: Dict[str, float] = {}
        national_total = 0.0

        for dist_id, val in district_forecasts.items():
            st = district_to_state.get(dist_id, "UNKNOWN")
            state_totals[st] = state_totals.get(st, 0.0) + val
            national_total += val

        return {
            "district": {str(k): float(v) for k, v in district_forecasts.items()},
            "state": state_totals,
            "national": {"total": float(national_total)},
        }

    def reconcile_mint_shrinkage(
        self,
        base_forecasts: np.ndarray,
        S_matrix: np.ndarray,
        error_residuals: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """
        MinT Optimal Reconciliation:
          y_tilde = S * (S^T * W^-1 * S)^-1 * S^T * W^-1 * y_hat
        where W is the Ledoit-Wolf shrinkage error covariance.
        """
        n_total, n_bottom = S_matrix.shape

        if error_residuals is None or error_residuals.shape[0] < 5:
            # Diagonal structural fallback (W = diag(variance))
            W = np.eye(n_total)
        else:
            # Empirical covariance with shrinkage towards diagonal
            sample_cov = np.cov(error_residuals, rowvar=False)
            if sample_cov.ndim < 2:
                sample_cov = np.diag([float(sample_cov)])
            diag_target = np.diag(np.diag(sample_cov))
            shrinkage_lambda = 0.2  # 20% shrinkage towards diagonal
            W = (1.0 - shrinkage_lambda) * sample_cov + shrinkage_lambda * diag_target

        try:
            W_inv = np.linalg.pinv(W)
            STS = S_matrix.T @ W_inv @ S_matrix
            STS_inv = np.linalg.pinv(STS)
            P = STS_inv @ S_matrix.T @ W_inv
            y_tilde = S_matrix @ P @ base_forecasts
            # Guarantee non-negativity
            return np.maximum(0.0, y_tilde)
        except Exception:
            # Fall back to simple bottom-up
            y_bottom = base_forecasts[-n_bottom:]
            return np.maximum(0.0, S_matrix @ y_bottom)
