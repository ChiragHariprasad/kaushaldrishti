"""
State-Space Demand Forecaster (Layer 6).
Projects the Kalman filter state (m_t, b_t, P_t) forward in time without new observations.
"""

from typing import Dict, List, Optional, Tuple, Union
import numpy as np


class StateSpaceForecaster:
    """
    Bayesian State-Space Forecaster.
    Projects the structural state (level m_t, drift b_t, variance P_t) forward over horizon h.
    
    Equations:
      m_{t+h} = m_t + sum_{i=1}^h (phi^i * b_t)
      P_{t+h} = P_t + h * Q_theta
      V_hat_{t+h} = exp(m_{t+h} + 0.5 * P_{t+h})
      sigma_h = sqrt(P_{t+h})
      q10 = exp(m_{t+h} - 1.2816 * sigma_h)
      q90 = exp(m_{t+h} + 1.2816 * sigma_h)
    """

    def __init__(self, phi: float = 0.95, q_theta: float = 0.04):
        """
        phi: Damped autoregressive trend factor (0 < phi <= 1.0)
        q_theta: Monthly process noise variance
        """
        self.phi = phi
        self.q_theta = q_theta

    def project_cell(
        self,
        m_t: float,
        b_t: float,
        p_t: float,
        horizon: int,
    ) -> Dict[str, np.ndarray]:
        """
        Project a single cell forward across horizons 1..horizon.
        Returns dict of arrays:
          'mean': Expected openings V_hat_{t+h}
          'log_mean': Expected log demand m_{t+h}
          'sigma': Log-scale standard deviation sigma_h
          'q10': 10th percentile openings
          'q90': 90th percentile openings
          'q025': 2.5th percentile openings
          'q975': 97.5th percentile openings
        """
        horizons = np.arange(1, horizon + 1)
        
        # Cumulative damped drift: sum_{i=1}^h phi^i
        if abs(self.phi - 1.0) < 1e-6:
            cum_drift = horizons * b_t
        else:
            cum_drift = b_t * np.array([
                np.sum([self.phi**i for i in range(1, h + 1)])
                for h in horizons
            ])
            
        m_proj = m_t + cum_drift
        p_proj = p_t + horizons * self.q_theta
        sigma_proj = np.sqrt(np.maximum(1e-4, p_proj))
        
        # Exponentiated openings (log-normal expectation E[exp(X)] = exp(mu + 0.5*sigma^2))
        v_mean = np.exp(np.clip(m_proj + 0.5 * p_proj, -5.0, 15.0))
        
        # Credible intervals
        q10 = np.exp(np.clip(m_proj - 1.2816 * sigma_proj, -5.0, 15.0))
        q90 = np.exp(np.clip(m_proj + 1.2816 * sigma_proj, -5.0, 15.0))
        q025 = np.exp(np.clip(m_proj - 1.96 * sigma_proj, -5.0, 15.0))
        q975 = np.exp(np.clip(m_proj + 1.96 * sigma_proj, -5.0, 15.0))
        
        return {
            "mean": v_mean,
            "log_mean": m_proj,
            "sigma": sigma_proj,
            "q10": q10,
            "q90": q90,
            "q025": q025,
            "q975": q975,
        }

    def forecast_horizon(
        self,
        m_t: float,
        b_t: float,
        p_t: float,
        h: int,
    ) -> Tuple[float, float, float]:
        """
        Forecast a specific horizon h.
        Returns (mean, q10, q90).
        """
        res = self.project_cell(m_t, b_t, p_t, h)
        return float(res["mean"][h - 1]), float(res["q10"][h - 1]), float(res["q90"][h - 1])
