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

## M3 — Supply Intelligence

| # | Decision | Rationale |
|---|----------|-----------|
| D-019 | Strict structural exclusion of placement data from supply | Prevents circularity and false supply suppression. Placement outcomes are only used for validation/scenario analysis, never in the definition of graduating supply. |
| D-020 | Beta-Binomial partial pooling for E, CR, Cert | Method of moments fits state-level prior; district centre cohorts update conjugate Beta distributions; product sampled with $\ge 2,000$ draws. |
| D-021 | Strict `capacity_based` labelling for unstarted cohorts | Uncommenced cohorts where only capacity/seats are known are never labelled "certified entrants", maintaining data honesty. |
| D-022 | Window supply dual tracking ($W=3$ and $W=12$) | $W=12$ window aligns with annual target-setting and cohort graduation cycles; $W=3$ supports quarterly monitoring. |

## M4 — Forecasting & Backtesting

| # | Decision | Rationale |
|---|----------|-----------|
| D-023 | Horizon-dependent volatility scaling in split-conformal calibration | Local volatility scaling with $\sqrt{h/6}$ horizon factor produces empirical 80% coverage within $[75\%, 85\%]$ ($\pm 5$ points of nominal target). |
| D-024 | Cohort-aligned horizon $h=L$ | Demand forecasting automatically evaluates horizon equal to course training duration $L$ (e.g. 12m for EV Tech, 6m for Solar Tech) so seat sanction cycles are evaluated when cohorts graduate. |
| D-025 | Hierarchical bottom-up MinT reconciliation | Reconciles district, state, and sector levels while ensuring non-negative vacancy guarantees and statistical consistency. |
| D-026 | Pinball loss minimization for ensemble weighting | Optimizes quantile-calibrated convex combination ($w_{ETS}, w_{Kalman}, w_{LGBM}$) rather than pure MSE, yielding tighter uncertainty bands. |

## M5 — Gap Analysis, Alerts & Explainability

| # | Decision | Rationale |
|---|----------|-----------|
| D-027 | Dynamic tolerance $\tau = \max(0.10 E[D], 5)$ | Scales tolerance with vacancy magnitude while guaranteeing minimum resolution floor of 5 seats in smaller districts. |
| D-028 | 2-refresh hysteresis state machine | Requires 2 consecutive refreshes to raise or escalate an alert; prevents transient flutter and decision chatter. |
| D-029 | Hysteresis de-escalation margin $(\text{threshold} - 0.10)$ | De-escalation from Acute Shortage requires probability falling below 0.70 for 2 consecutive cycles, stabilizing resource planning. |
| D-030 | Mutual exclusivity of shortage and saturation | Structurally prohibits inconsistent states; a trade in a district cannot simultaneously be flagged as in shortage and saturated. |
| D-031 | Deterministic multilingual explainability narratives | Templated natural language generation driven strictly by `glossary.csv` in `en`, `hi`, `kn`, `ta` without runtime LLM dependencies. |

## M6 & M8 — APIs, Lineage & Policy Simulator

| # | Decision | Rationale |
|---|----------|-----------|
| D-032 | Stock-flow delay simulator with explicit lags | Model enforces cohort training delay $L$ and facility commissioning delay $L_{build}$, prohibiting instantaneous supply creation. |
| D-033 | Automated multi-format export endpoint | Single `/api/v1/export` supporting CSV, XLSX, JSON, GeoJSON, and Parquet with automated schema validation. |
| D-034 | Cell-level lineage tracing (`/api/v1/lineage/{cell_id}`) | Provides end-to-end provenance: raw records $\to$ quality filters $\to$ Kalman weights $\to$ supply draws $\to$ alert state. |
| D-035 | Idempotent webhook delivery with HMAC verification | Supports asynchronous downstream integration with state skill portals with test endpoints and delivery logs. |

## M7 — Frontend Dashboard & Accessibility

| # | Decision | Rationale |
|---|----------|-----------|
| D-036 | Low-bandwidth semantic HTML fallback tables | Ensures accessibility in remote district offices with slow connectivity; fully navigable without WebGL or complex SVG. |
| D-037 | Interactive Golden Path navigation bar | Guiding banner allows evaluators to execute the complete SIH evaluation flow in $\le 3$ clicks per level. |
| D-038 | Printable 1-page executive district brief | `@media print` optimized layout with official MSDE branding for District Skill Development Officers (DSDO). |

