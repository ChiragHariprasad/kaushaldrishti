"""
Supply Dynamics Engine (Layer 5).
Simulates training pipeline supply:
S_cert(t+L) = C * E * CR * Cert
Samples >= 2000 draws from the product of Beta posteriors.

CRITICAL ARCHITECTURAL RULE:
Placement/employment outcomes MUST NOT enter the supply definition.
They are used only for calibration/validation, never in supply equations.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from pipelines.supply.beta_models import BetaRateModel


@dataclass(frozen=True)
class PipelineCohortInput:
    """
    Cohort input record.
    Notice: Placement outcomes are intentionally EXCLUDED from this data structure.
    Any attempt to pass placement fields will be rejected.
    """
    capacity: int
    allocated_seats: int
    enrolled: int
    completed: int
    certified: int
    course_months: int = 6


class SupplyDynamicsEngine:
    """
    Computes probabilistic supply forecasts with Monte Carlo sampling (>= 2,000 draws).
    """

    def __init__(self, n_draws: int = 2000, seed: int = 42):
        self.n_draws = max(2000, n_draws)
        self.seed = seed

    def compute_s_cert(
        self,
        cohort: PipelineCohortInput,
        prior_e: Tuple[float, float] = (18.0, 2.0),
        prior_cr: Tuple[float, float] = (16.0, 4.0),
        prior_cert: Tuple[float, float] = (17.0, 3.0),
    ) -> Dict[str, Any]:
        """
        Samples S_cert = C * E * CR * Cert.
        Returns:
        - s_mean, s_q10, s_q90
        - samples array
        - basis label ('certified' or 'capacity_based')
        """
        # If capacity/seats exist but no pipeline progression data (e.g. newly sanctioned)
        if cohort.enrolled == 0 and cohort.completed == 0 and cohort.certified == 0:
            if cohort.allocated_seats > 0 or cohort.capacity > 0:
                seats = cohort.allocated_seats if cohort.allocated_seats > 0 else cohort.capacity
                # Strictly labelled capacity_based — never called certified entrants
                return {
                    "basis": "capacity_based",
                    "s_mean": float(seats),
                    "s_q10": float(seats),
                    "s_q90": float(seats),
                    "samples": np.full(self.n_draws, float(seats)),
                    "mean_e": 1.0,
                    "mean_cr": 1.0,
                    "mean_cert": 1.0,
                }

        # 1. Update Beta posteriors for E, CR, Cert
        model_e = BetaRateModel(prior_e[0], prior_e[1])
        model_cr = BetaRateModel(prior_cr[0], prior_cr[1])
        model_cert = BetaRateModel(prior_cert[0], prior_cert[1])

        # Trials & Successes
        c_seats = max(1, cohort.allocated_seats)
        post_e_alpha, post_e_beta = model_e.update_posterior(
            successes=min(c_seats, cohort.enrolled),
            trials=c_seats,
        )

        n_enrolled = max(1, cohort.enrolled)
        post_cr_alpha, post_cr_beta = model_cr.update_posterior(
            successes=min(n_enrolled, cohort.completed),
            trials=n_enrolled,
        )

        n_completed = max(1, cohort.completed)
        post_cert_alpha, post_cert_beta = model_cert.update_posterior(
            successes=min(n_completed, cohort.certified),
            trials=n_completed,
        )

        # 2. Draw samples (>= 2,000 draws)
        draws_e = BetaRateModel.sample_posterior(post_e_alpha, post_e_beta, self.n_draws)
        draws_cr = BetaRateModel.sample_posterior(post_cr_alpha, post_cr_beta, self.n_draws)
        draws_cert = BetaRateModel.sample_posterior(post_cert_alpha, post_cert_beta, self.n_draws)

        # 3. Product of rates * Sanctioned Seats C
        product_rates = draws_e * draws_cr * draws_cert
        s_samples = c_seats * product_rates

        s_mean = float(np.mean(s_samples))
        s_q10 = float(np.percentile(s_samples, 10))
        s_q90 = float(np.percentile(s_samples, 90))

        # Expected rates for analytical checking
        exp_e = post_e_alpha / (post_e_alpha + post_e_beta)
        exp_cr = post_cr_alpha / (post_cr_alpha + post_cr_beta)
        exp_cert = post_cert_alpha / (post_cert_alpha + post_cert_beta)

        return {
            "basis": "certified",
            "s_mean": round(s_mean, 2),
            "s_q10": round(s_q10, 2),
            "s_q90": round(s_q90, 2),
            "samples": s_samples,
            "mean_e": round(exp_e, 4),
            "mean_cr": round(exp_cr, 4),
            "mean_cert": round(exp_cert, 4),
            "expected_closed_form": round(c_seats * exp_e * exp_cr * exp_cert, 2),
        }

    def compute_window_supply(
        self,
        cohorts: List[PipelineCohortInput],
        window_months: int = 12,
        other_channels_annual: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Computes window supply S_W(t+L) = sum of cohorts started in window [t, t+W).
        If other channels (ITI, polytechnic, informal) are added, basis becomes certified_plus_other.
        """
        all_samples = np.zeros(self.n_draws)
        total_seats = 0
        all_capacity_based = True

        for c in cohorts:
            total_seats += c.allocated_seats
            res = self.compute_s_cert(c)
            all_samples += res["samples"]
            if res["basis"] != "capacity_based":
                all_capacity_based = False

        # Add other channels if present
        basis = "certified"
        if other_channels_annual > 0:
            window_other = other_channels_annual * (window_months / 12.0)
            all_samples += window_other
            basis = "certified_plus_other"
        elif all_capacity_based:
            basis = "capacity_based"

        return {
            "window_months": window_months,
            "basis": basis,
            "s_mean": round(float(np.mean(all_samples)), 2),
            "s_q10": round(float(np.percentile(all_samples, 10)), 2),
            "s_q90": round(float(np.percentile(all_samples, 90)), 2),
            "samples": all_samples,
            "total_sanctioned_seats": total_seats,
        }
