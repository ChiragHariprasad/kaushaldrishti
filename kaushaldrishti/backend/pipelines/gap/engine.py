"""
Probabilistic Gap and Severity Engine (Layer 6).
Computes G = D_W(t+L) - S_W(t+L) using analytic and Monte Carlo distributions.
Calculates tolerance tau, probabilities (p_S, p_O, p_B), and bounded Severity (0-100).
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from scipy.stats import norm


class GapEngine:
    """
    Probabilistic Gap Engine.
    
    Formulas:
      G = D_W - S_W
      sigma_G = sqrt(sigma_D^2 + sigma_S^2)
      g = G / max(E[D], 1.0)
      tau = max(0.10 * E[D], 5.0)
      p_S = P(G > tau) = 1 - Phi((tau - E[G]) / sigma_G)
      p_O = P(G < -tau) = Phi((-tau - E[G]) / sigma_G)
      p_B = 1 - p_S - p_O
      Severity = 100 * p * min(1.0, |g| / 0.30)
    """

    def __init__(self, eps: float = 1.0):
        self.eps = eps

    def compute_tolerance(self, d_mean: float) -> float:
        """tau = max(0.10 * E[D], 5.0)"""
        return max(0.10 * float(d_mean), 5.0)

    def compute_cell_gap(
        self,
        d_mean: float,
        d_sigma: float,
        s_mean: float,
        s_sigma: float,
        window_months: int = 12,
    ) -> Dict[str, Any]:
        """
        Computes gap distribution, status, probabilities, and severity.
        """
        d_mean = max(0.0, float(d_mean))
        s_mean = max(0.0, float(s_mean))
        d_sigma = max(1e-4, float(d_sigma))
        s_sigma = max(1e-4, float(s_sigma))

        g_mean = d_mean - s_mean
        sigma_g = float(np.sqrt(d_sigma**2 + s_sigma**2))
        gap_rate = g_mean / max(d_mean, self.eps)
        tau = self.compute_tolerance(d_mean)

        # Probabilities via normal CDF
        z_s = (tau - g_mean) / sigma_g
        z_o = (-tau - g_mean) / sigma_g

        p_s = float(1.0 - norm.cdf(z_s))
        p_o = float(norm.cdf(z_o))
        p_b = float(np.clip(1.0 - p_s - p_o, 0.0, 1.0))

        # Status determination
        if p_s > 0.50 and g_mean > 0:
            status = "Shortage"
            p_active = p_s
        elif p_o > 0.50 and g_mean < 0:
            status = "Surplus"
            p_active = p_o
        else:
            status = "Balanced"
            p_active = p_b

        # Severity: 100 * p * min(1, |g| / 0.30)
        severity = float(np.clip(100.0 * p_active * min(1.0, abs(gap_rate) / 0.30), 0.0, 100.0))

        # Credible bounds on gap
        g_q10 = float(g_mean - 1.2816 * sigma_g)
        g_q90 = float(g_mean + 1.2816 * sigma_g)

        return {
            "window_months": window_months,
            "d_mean": round(d_mean, 2),
            "s_mean": round(s_mean, 2),
            "g_mean": round(g_mean, 2),
            "sigma_g": round(sigma_g, 2),
            "g_q10": round(g_q10, 2),
            "g_q90": round(g_q90, 2),
            "gap_rate": round(gap_rate, 4),
            "tolerance": round(tau, 2),
            "p_shortage": round(p_s, 4),
            "p_oversupply": round(p_o, 4),
            "p_balanced": round(p_b, 4),
            "status": status,
            "severity": round(severity, 1),
        }
