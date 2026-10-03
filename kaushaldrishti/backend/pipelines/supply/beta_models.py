"""
Beta-Binomial Models with Empirical Bayes Partial Pooling (Layer 5).
Fits Beta posteriors for training pipeline rates:
- E: Fill rate (enrolled / allocated_seats)
- CR: Completion rate (completed / enrolled)
- Cert: Certification rate (certified / completed)
State-trade prior fitted by method of moments; district-trade posterior pooled.
"""

from typing import Dict, List, Tuple
import numpy as np


class BetaRateModel:
    """
    Beta-Binomial model with empirical Bayes state-level prior.
    """

    def __init__(self, prior_alpha: float = 18.0, prior_beta: float = 2.0):
        self.prior_alpha = max(1.0, prior_alpha)
        self.prior_beta = max(1.0, prior_beta)

    @staticmethod
    def fit_method_of_moments(rates: List[float]) -> Tuple[float, float]:
        """
        Fits prior Beta(alpha, beta) using method of moments from an array of observed rates.
        mean = alpha / (alpha + beta)
        var = (alpha * beta) / ((alpha + beta)^2 * (alpha + beta + 1))
        """
        valid_rates = [float(r) for r in rates if 0.0 <= r <= 1.0]
        if len(valid_rates) < 3:
            return 18.0, 2.0  # Conservative high prior (0.90)

        mean = float(np.mean(valid_rates))
        var = float(np.var(valid_rates, ddof=1))

        # Ensure variance is within valid bounds for a Beta distribution: var < mean * (1 - mean)
        max_var = mean * (1.0 - mean)
        if var <= 0 or var >= max_var:
            var = max_var * 0.25

        common_factor = (mean * (1.0 - mean) / var) - 1.0
        alpha = max(1.0, mean * common_factor)
        beta = max(1.0, (1.0 - mean) * common_factor)

        return float(alpha), float(beta)

    def update_posterior(self, successes: int, trials: int) -> Tuple[float, float]:
        """
        Conjugate Beta-Binomial update:
        alpha_post = alpha_prior + successes
        beta_post = beta_prior + (trials - successes)
        """
        s = max(0, int(successes))
        n = max(s, int(trials))
        failures = n - s

        post_alpha = self.prior_alpha + s
        post_beta = self.prior_beta + failures
        return float(post_alpha), float(post_beta)

    @staticmethod
    def sample_posterior(post_alpha: float, post_beta: float, n_draws: int = 2000) -> np.ndarray:
        """
        Draws samples from Beta(post_alpha, post_beta).
        Guaranteed bounded in [0, 1].
        """
        samples = np.random.beta(max(1e-3, post_alpha), max(1e-3, post_beta), size=n_draws)
        return np.clip(samples, 0.0, 1.0)
