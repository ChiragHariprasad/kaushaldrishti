"""
Kalman Fusion Engine in Information Form (Layer 4).
Closed-form multi-source Bayesian fusion with exact source attribution,
empirical Bayes partial pooling across districts, and hierarchical fallback.
"""

import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class KalmanFusion:
    """
    Closed-form Kalman Filter in Information Form for a single cell (district, trade).
    """

    def __init__(
        self,
        phi: float = 0.9,
        q_theta: float = 0.04,  # Process noise for level
        q_b: float = 0.01,      # Process noise for slope
    ):
        self.phi = phi
        self.q_theta = q_theta
        self.q_b = q_b

    def predict(
        self,
        m_prev: float,
        p_prev: float,
        b_prev: float = 0.0,
    ) -> Tuple[float, float, float]:
        """
        Prior prediction step at time t:
        - m_{t|t-1} = m_{t-1} + b_{t-1}
        - b_{t|t-1} = phi * b_{t-1}
        - P_{t|t-1} = P_{t-1} + q_theta
        """
        m_prior = m_prev + b_prev
        b_prior = self.phi * b_prev
        p_prior = p_prev + self.q_theta
        return m_prior, p_prior, b_prior

    def update(
        self,
        m_prior: float,
        p_prior: float,
        observations: List[Dict[str, Any]],  # [{'source_id': str, 'z': float, 'v': float, 'gate_pass': bool}]
    ) -> Dict[str, Any]:
        """
        Information-form update:
        P_t^{-1} = P_{t|t-1}^{-1} + sum_k (v_k^{-1} * gate_pass_k)
        m_t = P_t * (P_{t|t-1}^{-1} * m_{t|t-1} + sum_k (z_k / v_k * gate_pass_k))

        Calculates exact source attributions:
        w_k = v_k^{-1} / P_t^{-1}
        contribution_k = w_k * (z_k - m_{t|t-1})
        """
        info_prior = 1.0 / max(1e-6, p_prior)
        total_info = info_prior
        weighted_sum = info_prior * m_prior

        gated_sources = [obs for obs in observations if obs.get("gate_pass", True)]

        # Sum information terms for gated sources
        for obs in gated_sources:
            v_k = max(1e-6, obs["v"])
            info_k = 1.0 / v_k
            total_info += info_k
            weighted_sum += info_k * obs["z"]

        # Posterior variance and mean
        p_post = 1.0 / total_info
        m_post = p_post * weighted_sum

        # Calculate exact attributions
        w_prior = info_prior / total_info
        contributions = []
        for obs in observations:
            if obs.get("gate_pass", True):
                v_k = max(1e-6, obs["v"])
                info_k = 1.0 / v_k
                w_k = info_k / total_info
                contrib_k = w_k * (obs["z"] - m_prior)
                contributions.append({
                    "source_id": obs["source_id"],
                    "weight": round(w_k, 5),
                    "contribution": round(contrib_k, 5),
                    "z": obs["z"],
                    "v": obs["v"],
                    "gate_pass": True,
                })
            else:
                contributions.append({
                    "source_id": obs["source_id"],
                    "weight": 0.0,
                    "contribution": 0.0,
                    "z": obs.get("z", 0.0),
                    "v": obs.get("v", 1.0),
                    "gate_pass": False,
                    "gate_reason": obs.get("gate_reason", "gated_out"),
                })

        return {
            "m_post": float(m_post),
            "p_post": float(p_post),
            "m_prior": float(m_prior),
            "p_prior": float(p_prior),
            "prior_weight": round(w_prior, 5),
            "contributions": contributions,
            "n_gated": len(gated_sources),
        }

    @staticmethod
    def apply_partial_pooling(
        district_m: float,
        district_p: float,
        state_m: float,
        tau2: float,
    ) -> Tuple[float, float, float, float]:
        """
        Partial pooling with Empirical Bayes shrinkage:
        - lambda = tau^{-2} / (tau^{-2} + P_{data}^{-1})
        - omega = 1 - lambda (data share)
        - m_pooled = (1 - lambda) * district_m + lambda * state_m
        - P_pooled^{-1} = P_{data}^{-1} + tau^{-2}
        """
        if tau2 <= 1e-6:
            # Complete pooling toward state level
            return float(state_m), float(district_p), 1.0, 0.0

        p_inv = 1.0 / max(1e-6, district_p)
        tau_inv = 1.0 / tau2

        total_precision = p_inv + tau_inv
        shrinkage_lambda = tau_inv / total_precision
        data_share_omega = 1.0 - shrinkage_lambda

        m_pooled = (data_share_omega * district_m) + (shrinkage_lambda * state_m)
        p_pooled = 1.0 / total_precision

        return (
            float(m_pooled),
            float(p_pooled),
            float(shrinkage_lambda),
            float(data_share_omega),
        )

    @staticmethod
    def estimate_tau2(district_means: List[float], district_variances: List[float]) -> float:
        """
        Empirical Bayes estimate of between-district variance tau^2:
        tau^2 = max(0, Var_d(m) - mean(P))
        """
        if len(district_means) < 2:
            return 0.25  # Prior default
        var_m = float(np.var(district_means, ddof=1))
        mean_p = float(np.mean(district_variances))
        tau2 = max(0.001, var_m - mean_p)
        return float(tau2)
