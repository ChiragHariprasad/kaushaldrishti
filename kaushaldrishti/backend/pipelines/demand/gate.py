"""
Reliability Gate & Factor Calculation (Layer 4).
Evaluates coverage, freshness, stability, and consensus agreement.
Calculates dynamic source reliability factor r_k.
"""

import math
from typing import Dict, List, Optional, Tuple

import numpy as np


class ReliabilityGate:
    """
    Gates evidence per source/cell and calculates r_k.
    """

    def __init__(
        self,
        n_eff_min: float = 10.0,
        max_age_multiplier: float = 2.0,
        max_mad: float = 2.5,
        max_consensus_deviation: float = 3.0,
        min_agree_months: int = 4,
    ):
        self.n_eff_min = n_eff_min
        self.max_age_multiplier = max_age_multiplier
        self.max_mad = max_mad
        self.max_consensus_deviation = max_consensus_deviation
        self.min_agree_months = min_agree_months

    def evaluate_gate(
        self,
        n_eff_trailing_90d: float,
        age_days: float,
        nominal_update_days: int,
        residuals_history: Optional[List[float]] = None,
        leave_one_out_deviations: Optional[List[float]] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Evaluates 4 gate criteria:
        1. Coverage: n_eff >= 10 in trailing 90d
        2. Freshness: age <= 2 * nominal_update_days
        3. Stability: MAD of standardized residuals <= 2.5
        4. Agreement: consensus deviation <= 3.0 in at least 4 of last 6 months
        """
        # 1. Coverage
        if n_eff_trailing_90d < self.n_eff_min:
            return False, f"Coverage insufficient: n_eff ({n_eff_trailing_90d:.1f}) < {self.n_eff_min}"

        # 2. Freshness
        max_allowed_age = self.max_age_multiplier * nominal_update_days
        if age_days > max_allowed_age:
            return False, f"Stale source: age ({age_days:.1f}d) > max allowed ({max_allowed_age:.1f}d)"

        # 3. Stability (MAD of standardized residuals)
        if residuals_history and len(residuals_history) >= 4:
            res_arr = np.array(residuals_history)
            median_res = np.median(res_arr)
            mad = float(np.median(np.abs(res_arr - median_res))) * 1.4826  # Normal scale factor
            if mad > self.max_mad:
                return False, f"Instability detected: MAD ({mad:.2f}) > {self.max_mad}"

        # 4. Consensus Agreement (leave-one-out)
        if leave_one_out_deviations and len(leave_one_out_deviations) >= 6:
            agree_count = sum(1 for dev in leave_one_out_deviations[-6:] if abs(dev) <= self.max_consensus_deviation)
            if agree_count < self.min_agree_months:
                return False, f"Consensus disagreement: only {agree_count}/6 months agreed"

        return True, None

    @staticmethod
    def calculate_r_k(
        v_bar_k: float,
        loo_deviations: List[float],
    ) -> float:
        """
        Computes dynamic reliability r_k = clip(vbar_k / MSE_k, 0.1, 1.0).
        Where MSE_k is the rolling mean of excess squared leave-one-out deviation (floored at vbar_k).
        """
        if not loo_deviations:
            return 1.0

        sq_devs = [d ** 2 for d in loo_deviations]
        mse_k = float(np.mean(sq_devs))
        effective_mse = max(v_bar_k, mse_k)

        r_k = v_bar_k / effective_mse
        return float(np.clip(r_k, 0.1, 1.0))
