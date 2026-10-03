"""
Labour Demand Index (LDI) and Driver Descriptors (Layer 4).
Computes population-standardized demand intensity iota, maps to 0-100 LDI via frozen baseline CDF,
computes 6 driver descriptors (V, G, R, P_persist, B, I), and assigns confidence badges.
"""

import bisect
import json
import math
import os
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class DemandIndexEngine:
    """
    Computes LDI against frozen baseline and evaluates driver descriptors.
    """

    def __init__(self, baseline_config_path: Optional[str] = None):
        if not baseline_config_path:
            baseline_config_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..", "..", "config", "baseline.json")
            )
        self.baseline_path = baseline_config_path
        self.trade_baseline_cdfs: Dict[str, List[float]] = self._load_or_init_baseline()

    def _load_or_init_baseline(self) -> Dict[str, List[float]]:
        """Loads frozen baseline intensity CDFs per trade."""
        cdfs = {}
        if os.path.exists(self.baseline_path):
            try:
                with open(self.baseline_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "trade_cdfs" in data:
                        cdfs = {k: sorted(v) for k, v in data["trade_cdfs"].items()}
            except Exception:
                pass
        return cdfs

    def save_frozen_baseline(self, trade_intensities_map: Dict[str, List[float]]) -> None:
        """Saves frozen baseline CDFs for 24-month reference period."""
        cdfs = {k: sorted(v) for k, v in trade_intensities_map.items()}
        self.trade_baseline_cdfs = cdfs
        payload = {
            "version": 1,
            "description": "Frozen 24-month baseline (2021-01 to 2022-12) for LDI scoring.",
            "window_start": "2021-01",
            "window_end": "2022-12",
            "trade_cdfs": cdfs,
        }
        with open(self.baseline_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def compute_intensity(self, m: float, population_working_age: int) -> float:
        """
        Computes demand intensity per 100,000 working-age population:
        iota = m - ln(pop_working_age / 100,000)
        """
        pop_scale = max(1000.0, float(population_working_age)) / 100000.0
        return float(m - math.log(pop_scale))

    def evaluate_cdf_percentile(self, trade_name: str, iota: float) -> float:
        """
        Maps intensity iota to percentile [0, 100] using frozen baseline empirical CDF.
        If baseline not yet populated, uses standard normal CDF approximation around mu=3.0, sigma=0.8.
        """
        cdf_values = self.trade_baseline_cdfs.get(trade_name)
        if cdf_values and len(cdf_values) > 10:
            # Empirical CDF with linear interpolation
            idx = bisect.bisect_left(cdf_values, iota)
            pct = (idx / len(cdf_values)) * 100.0
            return float(np.clip(pct, 0.5, 99.5))
        else:
            # Calibrated parametric fallback (mean ~ 3.0, std ~ 0.8)
            z = (iota - 3.0) / 0.85
            # Sigmoid / probit approximation
            prob = 1.0 / (1.0 + math.exp(-1.702 * z))
            return float(np.clip(prob * 100.0, 1.0, 99.0))

    def compute_ldi(
        self,
        trade_name: str,
        m: float,
        p: float,
        population_working_age: int,
    ) -> Tuple[float, float, float, float]:
        """
        Computes (intensity_iota, ldi, ldi_lo, ldi_hi) using 80% credible interval (z=1.2816).
        """
        iota = self.compute_intensity(m, population_working_age)
        std_p = math.sqrt(max(1e-6, p))
        iota_lo = iota - (1.2816 * std_p)
        iota_hi = iota + (1.2816 * std_p)

        ldi = self.evaluate_cdf_percentile(trade_name, iota)
        ldi_lo = self.evaluate_cdf_percentile(trade_name, iota_lo)
        ldi_hi = self.evaluate_cdf_percentile(trade_name, iota_hi)

        return (
            round(iota, 4),
            round(ldi, 1),
            round(min(ldi, ldi_lo), 1),
            round(max(ldi, ldi_hi), 1),
        )

    @staticmethod
    def compute_descriptors(
        m: float,
        m_history: List[float],
        source_weights: Dict[str, float],
        source_ages_days: Dict[str, float],
        source_growth_signs: Dict[str, int],  # 1 for positive growth, -1 for negative
        source_independence_groups: Dict[str, str],
        employer_counts: Optional[Dict[str, int]] = None,
    ) -> Dict[str, Any]:
        """
        Computes 6 driver descriptors:
        - V: Expected openings = exp(m)
        - G: 3-month annualized log slope %
        - R: Recency index = sum_k w_k exp(-age_k / 30)
        - P_persist: Months since growth sign change (cap 12)
        - B: Breadth (effective employers, inverse Herfindahl over 90d)
        - I: Corroboration score (share of independent gated sources agreeing in direction)
        """
        # 1. Volume (V)
        V = float(math.exp(m))

        # 2. Growth (G) - 3-month annualized %
        if len(m_history) >= 4:
            log_change_3m = m - m_history[-4]
            # Annualize by multiplying by 4 (4 quarters)
            G = float(log_change_3m * 4.0 * 100.0)
        else:
            G = 0.0

        # 3. Recency (R)
        R = 0.0
        for src_id, w in source_weights.items():
            age = source_ages_days.get(src_id, 30.0)
            R += w * math.exp(-age / 30.0)

        # 4. Growth Persistence (P_persist)
        P_persist = 1
        if len(m_history) >= 2:
            current_diff = m - m_history[-1]
            current_sign = 1 if current_diff >= 0 else -1
            for i in range(len(m_history) - 2, -1, -1):
                prev_diff = m_history[i+1] - m_history[i]
                prev_sign = 1 if prev_diff >= 0 else -1
                if prev_sign == current_sign:
                    P_persist += 1
                else:
                    break
        P_persist = min(12, P_persist)

        # 5. Breadth (B) - Inverse Herfindahl
        if employer_counts and sum(employer_counts.values()) > 0:
            total_emp = sum(employer_counts.values())
            shares = [c / total_emp for c in employer_counts.values()]
            hhi = sum(s ** 2 for s in shares)
            B = float(1.0 / max(1e-4, hhi))
        else:
            B = 5.0  # Reasonable default breadth

        # 6. Corroboration (I) across independent groups
        group_directions = {}
        for src_id, group in source_independence_groups.items():
            if src_id in source_growth_signs:
                group_directions[group] = source_growth_signs[src_id]

        if len(group_directions) >= 2:
            pos_count = sum(1 for d in group_directions.values() if d > 0)
            neg_count = sum(1 for d in group_directions.values() if d < 0)
            majority = max(pos_count, neg_count)
            I = float(majority / len(group_directions))
        else:
            I = 0.5  # Neutral when corroboration not possible

        return {
            "V": round(V, 2),
            "G": round(G, 2),
            "R": round(R, 3),
            "P_persist": int(P_persist),
            "B": round(B, 1),
            "I": round(I, 3),
        }

    @staticmethod
    def assign_confidence(
        p: float,
        data_share: float,
        n_independent_sources: int,
        fallback_level: int = 0,
    ) -> str:
        """
        Assigns High, Medium, or Low confidence badge based on config/confidence.yaml rules.
        """
        sqrt_p = math.sqrt(max(1e-6, p))

        # Rule 1: High
        if (
            sqrt_p <= 0.35
            and data_share >= 0.65
            and n_independent_sources >= 3
            and fallback_level == 0
        ):
            return "High"

        # Rule 2: Medium
        if (
            sqrt_p <= 0.65
            and data_share >= 0.35
            and n_independent_sources >= 2
            and fallback_level <= 1
        ):
            return "Medium"

        return "Low"
