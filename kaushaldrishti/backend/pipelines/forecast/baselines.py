"""
Baseline Forecasting Models (Layer 6).
Implements Seasonal Naive and Exponential Smoothing (ETS) benchmarks.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np


class SeasonalNaiveForecaster:
    """
    Seasonal Naive forecaster:
    Forecast at horizon h equals the observation from same season last year (lag-12).
    """

    def __init__(self, season_length: int = 12):
        self.season_length = season_length

    def forecast(self, history: List[float], horizon: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Returns (point_forecasts, std_errors).
        """
        if len(history) < self.season_length:
            last_val = history[-1] if history else 0.0
            return np.full(horizon, last_val), np.full(horizon, 0.4)

        forecasts = []
        for h in range(1, horizon + 1):
            lag_idx = -self.season_length + ((h - 1) % self.season_length)
            forecasts.append(history[lag_idx])

        diffs = [
            history[i] - history[i - self.season_length]
            for i in range(self.season_length, len(history))
        ]
        diff_std = float(np.std(diffs)) if len(diffs) > 1 else 0.35
        sigma = max(0.1, diff_std)

        # Uncertainty expands with horizon sqrt(ceil(h / season_length))
        stds = [sigma * np.sqrt(max(1.0, np.ceil(h / self.season_length))) for h in range(1, horizon + 1)]

        return np.array(forecasts), np.array(stds)


class SimpleETSForecaster:
    """
    Exponential Smoothing (Holt-Winters level + additive trend + additive season).
    """

    def __init__(self, alpha: float = 0.3, beta: float = 0.1, gamma: float = 0.2, season_len: int = 12):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.season_len = season_len

    def forecast(self, history: List[float], horizon: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fits Holt-Winters on history and projects horizon h forward.
        """
        n = len(history)
        if n < self.season_len * 2:
            # Fall back to Holt linear
            lvl = history[-1]
            slope = (history[-1] - history[0]) / max(1, n)
            preds = [lvl + (h * slope) for h in range(1, horizon + 1)]
            stds = [0.3 * np.sqrt(h) for h in range(1, horizon + 1)]
            return np.array(preds), np.array(stds)

        # Initialize components
        level = float(np.mean(history[:self.season_len]))
        trend = float((history[self.season_len] - history[0]) / self.season_len)
        seasonals = [history[i] - level for i in range(self.season_len)]

        residuals = []
        for t in range(self.season_len, n):
            val = history[t]
            s_idx = t % self.season_len
            pred = level + trend + seasonals[s_idx]
            res = val - pred
            residuals.append(res)

            prev_level = level
            level = self.alpha * (val - seasonals[s_idx]) + (1 - self.alpha) * (level + trend)
            trend = self.beta * (level - prev_level) + (1 - self.beta) * trend
            seasonals[s_idx] = self.gamma * (val - level) + (1 - self.gamma) * seasonals[s_idx]

        sigma = float(np.std(residuals)) if len(residuals) > 2 else 0.25

        forecasts = []
        stds = []
        for h in range(1, horizon + 1):
            s_idx = (n + h - 1) % self.season_len
            f_val = level + (h * trend) + seasonals[s_idx]
            forecasts.append(f_val)
            stds.append(sigma * np.sqrt(1 + 0.1 * h))

        return np.array(forecasts), np.array(stds)
