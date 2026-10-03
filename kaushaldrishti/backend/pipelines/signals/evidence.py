"""
Evidence Unit Construction (Layer 3).
Computes n_eff, coverage/seasonal corrections, log transformation, variance estimation,
and alpha/beta calibration to anchor scale.
"""

import math
from typing import Any, Dict, Optional, Tuple

import numpy as np


class EvidenceUnitBuilder:
    """
    Constructs calibrated evidence units for source k and cell (month, district, trade).
    """

    def __init__(
        self,
        sigma2_cov_k: float = 0.05,
        sigma2_dup_k: float = 0.02,
        alpha_k: float = 0.0,
        beta_k: float = 1.0,
    ):
        self.sigma2_cov_k = sigma2_cov_k
        self.sigma2_dup_k = sigma2_dup_k
        self.alpha_k = alpha_k
        self.beta_k = beta_k

    def build_evidence(
        self,
        n_eff: float,
        seasonal_factor: float = 1.0,
        coverage_ratio: float = 1.0,
        r_k: float = 1.0,
    ) -> Dict[str, float]:
        """
        Computes evidence parameters:
        - o_hat = n_eff / (seasonal_factor * coverage_ratio)
        - y = ln(o_hat + 0.5)
        - sigma2 = 1/(n_eff + 1) + sigma2_cov + sigma2_dup
        - z = (y - alpha_k) / beta_k
        - v = sigma2 / (r_k * beta_k^2)
        """
        denom = max(1e-4, seasonal_factor * coverage_ratio)
        o_hat = n_eff / denom

        y = math.log(o_hat + 0.5)
        sigma2 = (1.0 / (n_eff + 1.0)) + self.sigma2_cov_k + self.sigma2_dup_k

        # Calibrated observation and observation variance
        beta_safe = max(1e-3, self.beta_k)
        z = (y - self.alpha_k) / beta_safe

        r_safe = max(0.1, min(1.0, r_k))
        v = sigma2 / (r_safe * (beta_safe ** 2))

        return {
            "n_eff": float(n_eff),
            "o_hat": float(o_hat),
            "y_log": float(y),
            "sigma2": float(sigma2),
            "alpha": float(self.alpha_k),
            "beta": float(self.beta_k),
            "z": float(z),
            "v": float(v),
            "r_k": float(r_safe),
        }
