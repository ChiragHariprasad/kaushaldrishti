# Architecture and Design Decisions

This document records every non-obvious default chosen during implementation.

## M0 — Scaffold

| # | Decision | Rationale |
|---|----------|-----------|
| D-001 | SQLite fallback for unit tests | Avoids requiring PostgreSQL for CI/local testing. PostGIS-specific features tested only in integration. |
| D-002 | Nginx as reverse proxy on port 80 | Single entry point for the demo; API on /api/, frontend on /. |
| D-003 | `dev-key-2026` as default API key | Development convenience. Must be changed via `API_KEY` env var in production. |
| D-004 | Docker Compose v3.9 | Supports `service_healthy` condition for ordered startup. |
| D-005 | `pydantic-settings` for config | Type-safe env var loading with defaults, matching the Pydantic v2 ecosystem. |

## M1 — Data + Taxonomy

| # | Decision | Rationale |
|---|----------|-----------|
| D-006 | Indicative NCO codes marked `verified: false` | Strictly enforces Rule 7: Never invent official codes. Real official codes loaded via NCO seed file when available. |
| D-007 | Deterministic synthetic generator seed = 42 | Full reproducibility for backtests, benchmark comparisons, and seeded demo paths. |
| D-008 | 30 planted episodes (15 shortages, 15 saturations) | Gives verifiable precision/recall/lead-time ground truth for pipeline validation without claiming real-world accuracy. |
| D-009 | Sigmoid-calibrated taxonomy confidence | Maps raw multi-token and alias similarity to well-calibrated probabilities in [0, 1]. |
| D-010 | Taxonomy review queue threshold = 0.55 | Matches specifications; matches with confidence < 0.55 enter human-in-the-loop review queue. |
| D-011 | Exact match + Levenshtein distance for geography | Avoids token substring false positives (e.g. 'Prayagraj' vs 'Agra') while handling transliterations and colloquial aliases. |
| D-012 | Pydantic data contract string coercion | Handles pandas reading numerical codes (e.g. NCO 7231.0101) as floats without failing validation. |
| D-013 | Non-blocking adapter loading | Missing raw incoming files trigger clear warning and fall back to synthetic parquet (`data_mode: synthetic`), preventing pipeline crashes. |

## M2 — Demand Intelligence

| # | Decision | Rationale |
|---|----------|-----------|
| D-014 | Information-form Kalman filter formulation | Closed-form Bayesian update that naturally accommodates missing sources without imputation and computes exact source attribution weights. |
| D-015 | Empirical Bayes partial pooling across districts | Shrinks small-district estimates toward state mean ($\tau_s^2 = \max(0.001, \text{Var}_d(m) - \text{mean}(P))$), reporting data share $\omega = 1 - \lambda$. |
| D-016 | Frozen 24-month baseline CDF in `config/baseline.json` | Freezes baseline intensity distribution over the first 24 months so LDI (0–100) measures absolute progress rather than floating relative ranks. |
| D-017 | Separate index scale vs gap scale | Absolute log-openings scale ($m$) is used for supply/demand gap calculations; population-adjusted intensity ($\iota$) is used for cross-district LDI comparison. |
| D-018 | Dynamic reliability factor $r_k = \text{clip}(\bar{v}_k / \text{MSE}_k, 0.1, 1.0)$ | Penalizes sources that exhibit high leave-one-out consensus disagreement or sudden noise spikes by inflating their observation variance $v$. |
