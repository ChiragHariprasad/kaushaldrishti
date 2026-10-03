"""
Policy Scenario Simulator Engine (Layer 7).
Simulates stock-flow training pipeline dynamics with discrete cohort delays:
  S(t) = sum_c C_c' * E_c * (CR_c + dCR) * Cert_c * 1[t_c + L = t]
  with C_c' = C_c * (1 + seat_delta_pct) for cohorts from start_cycle.
Evaluates baseline vs intervention supply, demand paths, gap closure cycle, and net impact.
"""

import math
from typing import Any, Dict, List, Optional
import numpy as np


class PolicyScenarioSimulator:
    """
    Simulates policy interventions on district-trade vocational pipelines.
    
    Inputs:
      - seat_delta_pct: Seat expansion/contraction percentage (-0.50 to +0.50)
      - completion_delta_pp: Completion rate percentage point change (e.g. +0.05)
      - new_centre_capacity: Additional seats from a new training centre
      - new_centre_build_lag_months: Construction/licensing delay before new centre opens
      - demand_case: 'base' (median), 'high' (q80/q90), or 'low' (q10/q20)
      - simulation_months: Forecast window forward (default 24 months)
    """

    def __init__(self, simulation_months: int = 24):
        self.simulation_months = simulation_months

    def simulate(
        self,
        base_demand: float,
        demand_sigma: float,
        base_capacity: int,
        fill_rate: float,
        completion_rate: float,
        cert_rate: float,
        course_months: int,
        seat_delta_pct: float = 0.15,
        completion_delta_pp: float = 0.0,
        new_centre_capacity: int = 0,
        new_centre_build_lag_months: int = 6,
        demand_case: str = "base",
        start_month_str: str = "2025-01",
    ) -> Dict[str, Any]:
        """
        Executes discrete-time stock-flow cohort simulation.
        """
        L = max(1, int(course_months))
        seat_delta_pct = float(np.clip(seat_delta_pct, -0.50, 0.50))
        new_cr = float(np.clip(completion_rate + completion_delta_pp, 0.10, 0.99))
        fill_rate = float(np.clip(fill_rate, 0.10, 1.0))
        cert_rate = float(np.clip(cert_rate, 0.10, 1.0))

        # Monthly demand rate
        monthly_base_d = max(1.0, base_demand / 12.0)
        monthly_sigma_d = max(0.1, demand_sigma / math.sqrt(12.0))

        if demand_case == "high":
            monthly_d = monthly_base_d + 1.2816 * monthly_sigma_d
        elif demand_case == "low":
            monthly_d = max(0.0, monthly_base_d - 1.2816 * monthly_sigma_d)
        else:
            monthly_d = monthly_base_d

        # Monthly capacity allocation
        base_monthly_cap = max(1.0, base_capacity / 12.0)
        sim_monthly_cap = base_monthly_cap * (1.0 + seat_delta_pct)

        # Baseline throughput per cohort: C * E * CR * Cert
        baseline_cohort_output = base_monthly_cap * fill_rate * completion_rate * cert_rate

        # Simulation paths
        months = []
        baseline_supply_path = []
        intervention_supply_path = []
        demand_path = []
        baseline_gap_path = []
        intervention_gap_path = []

        start_year, start_m = map(int, start_month_str.split("-"))
        closing_cycle = None

        for t in range(self.simulation_months):
            # Calendar month formatting
            curr_y = start_year + (start_m - 1 + t) // 12
            curr_m = (start_m - 1 + t) % 12 + 1
            m_label = f"{curr_y}-{curr_m:02d}"
            months.append(m_label)

            # Demand at month t
            d_t = monthly_d
            demand_path.append(round(d_t, 1))

            # Baseline supply at month t
            s_base_t = baseline_cohort_output
            baseline_supply_path.append(round(s_base_t, 1))
            g_base_t = d_t - s_base_t
            baseline_gap_path.append(round(g_base_t, 1))

            # Intervention supply with cohort delay L
            if t < L:
                # Still graduating pre-intervention cohorts
                s_interv_t = s_base_t
            else:
                # Graduating cohorts that started under intervention
                cohort_cap = sim_monthly_cap
                # Add new centre capacity if construction delay has elapsed
                cohort_start_t = t - L
                if cohort_start_t >= new_centre_build_lag_months:
                    cohort_cap += (new_centre_capacity / 12.0)

                s_interv_t = cohort_cap * fill_rate * new_cr * cert_rate

            intervention_supply_path.append(round(s_interv_t, 1))
            g_interv_t = d_t - s_interv_t
            intervention_gap_path.append(round(g_interv_t, 1))

            # Check gap closure (intervention gap becomes <= 0 while baseline gap was > 0)
            if closing_cycle is None and t >= L:
                if g_interv_t <= 0.05 * d_t:  # Within 5% tolerance
                    closing_cycle = m_label

        # Net cumulative additions
        tot_base_supply = sum(baseline_supply_path)
        tot_interv_supply = sum(intervention_supply_path)
        net_additional_graduates = max(0, tot_interv_supply - tot_base_supply)

        return {
            "parameters": {
                "seat_delta_pct": seat_delta_pct,
                "completion_delta_pp": completion_delta_pp,
                "new_centre_capacity": new_centre_capacity,
                "new_centre_build_lag_months": new_centre_build_lag_months,
                "demand_case": demand_case,
                "course_months": L,
                "start_month": start_month_str,
            },
            "summary": {
                "closing_cycle": closing_cycle or "Does not close within 24 months",
                "gap_closed": closing_cycle is not None,
                "net_additional_graduates": round(net_additional_graduates, 0),
                "baseline_total_supply": round(tot_base_supply, 0),
                "intervention_total_supply": round(tot_interv_supply, 0),
                "pipeline_lag_months": L,
            },
            "series": {
                "months": months,
                "demand": demand_path,
                "baseline_supply": baseline_supply_path,
                "intervention_supply": intervention_supply_path,
                "baseline_gap": baseline_gap_path,
                "intervention_gap": intervention_gap_path,
            },
            "assumptions": [
                f"Course cohort pipeline duration is {L} months (graduates emerge t+{L}).",
                f"Fill rate remains stable at {fill_rate * 100:.1f}%.",
                f"Completion rate shifts from {completion_rate * 100:.1f}% to {new_cr * 100:.1f}%.",
                f"Certification rate is {cert_rate * 100:.1f}%.",
                f"Demand case '{demand_case}' evaluates {'median forecast' if demand_case == 'base' else ('q80 upside' if demand_case == 'high' else 'q20 downside')}.",
                "Placement data is structurally excluded to prevent circular bias.",
            ],
        }
