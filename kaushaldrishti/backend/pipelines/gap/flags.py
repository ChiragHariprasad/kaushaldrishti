"""
Early Warning Flags and Hysteresis State Machine (Layer 6).
Evaluates Acute/Emerging Shortages, Approaching Saturation, Saturated, and Stable states.
Implements 2-refresh persistence and de-escalation margins to prevent flickering.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class CellSignalInput:
    p_shortage: float
    p_oversupply: float
    gap_rate: float
    expected_gap: float
    demand_trend: float      # QoQ demand growth %
    capacity_trend: float    # QoQ capacity growth %
    confidence: str          # 'High', 'Medium', 'Low'
    interval_spread: float   # (q90 - q10) / max(1.0, |E[D]|)
    corroboration_i: float   # Independent corroborating sources
    national_p90_growth: float = 0.25


class HysteresisAlertManager:
    """
    Manages flag transitions with hysteresis.
    Rules:
      1. Raise/escalate only when candidate condition holds for 2 consecutive refreshes.
      2. Clear/de-escalate only when probability stays below (threshold - 0.10) for 2 consecutive refreshes.
      3. Shortage and Saturation are mutually exclusive.
      4. Overlays: 'Rapid Growth', 'Volatile'.
    """

    def __init__(self, de_escalate_margin: float = 0.10):
        self.de_escalate_margin = de_escalate_margin

    def evaluate_candidate_flag(self, sig: CellSignalInput) -> Tuple[str, List[str]]:
        """
        Determines instantaneous candidate flag and overlays for current refresh.
        """
        candidate = "Stable"
        overlays = []

        # Check Overlays first
        if sig.interval_spread > 1.0 or sig.confidence == "Low":
            overlays.append("Volatile")

        if sig.demand_trend >= sig.national_p90_growth and sig.corroboration_i >= 2.0:
            overlays.append("Rapid Growth")

        # Mutually exclusive flag evaluation: Shortage vs Saturation
        if sig.p_shortage >= 0.80 and sig.gap_rate >= 0.20:
            # Low confidence cells display Emerging Shortage or Volatile rather than Acute
            if sig.confidence == "Low":
                candidate = "Emerging Shortage"
            else:
                candidate = "Acute Shortage"
        elif (
            0.60 <= sig.p_shortage < 0.80
            and sig.demand_trend > 0
            and sig.capacity_trend <= 0.5 * sig.demand_trend
        ):
            candidate = "Emerging Shortage"
        elif sig.p_oversupply >= 0.80 and sig.gap_rate <= -0.20:
            candidate = "Saturated"
        elif 0.60 <= sig.p_oversupply < 0.80 and sig.capacity_trend > sig.demand_trend:
            candidate = "Approaching Saturation"
        else:
            candidate = "Stable"

        return candidate, overlays

    def step(
        self,
        current_flag: str,
        persistence_count: int,
        sig: CellSignalInput,
    ) -> Tuple[str, int, List[str], Optional[str]]:
        """
        Advances the hysteresis state machine by one refresh.
        Returns:
          (new_flag, new_persistence_count, overlays, transition_reason_or_None)
        """
        candidate, overlays = self.evaluate_candidate_flag(sig)

        # Case 1: Candidate matches current flag -> reinforce persistence
        if candidate == current_flag:
            return current_flag, persistence_count + 1, overlays, None

        # Check de-escalation condition if candidate is Stable
        clear_threshold = 0.50
        if current_flag == "Acute Shortage":
            clear_threshold = 0.80 - self.de_escalate_margin
            prob_metric = sig.p_shortage
        elif current_flag == "Emerging Shortage":
            clear_threshold = 0.60 - self.de_escalate_margin
            prob_metric = sig.p_shortage
        elif current_flag == "Saturated":
            clear_threshold = 0.80 - self.de_escalate_margin
            prob_metric = sig.p_oversupply
        elif current_flag == "Approaching Saturation":
            clear_threshold = 0.60 - self.de_escalate_margin
            prob_metric = sig.p_oversupply
        else:
            prob_metric = 0.0

        # If attempting to de-escalate to Stable, check probability margin
        if candidate == "Stable" and current_flag != "Stable":
            if prob_metric >= clear_threshold:
                # Metric hasn't dropped below de-escalation margin: retain flag
                return current_flag, persistence_count + 1, overlays, None

        # State transition requires 2 consecutive refreshes
        if persistence_count < 1:
            # First refresh meeting new candidate condition: hold current state, start candidate counter at 1
            return current_flag, 1, overlays, None

        # Second consecutive refresh meeting candidate condition: confirm transition
        if candidate == "Stable":
            reason = f"Metric {prob_metric:.2f} fell below de-escalation margin {clear_threshold:.2f} for 2 refreshes"
        else:
            reason = f"Candidate condition {candidate} persisted for 2 consecutive refreshes"

        return candidate, 1, overlays, reason
