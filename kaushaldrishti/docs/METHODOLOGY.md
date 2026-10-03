# Methodology — Labour Demand Index (LDI)

*Full methodology documentation will be added in M2 (Demand Intelligence).*

## Overview

KaushalDrishti computes a **Labour Demand Index (LDI)** for each district–trade cell using a closed-form Kalman fusion of multiple data sources. The index is comparable across districts via population-adjusted intensity scoring against a frozen baseline.

## Layers

1. **Evidence Unit Construction** — per source, per cell
2. **Reliability Gate** — coverage, freshness, stability, agreement
3. **Kalman Fusion** — information-form update with exact source attribution
4. **Partial Pooling** — empirical Bayes shrinkage across districts
5. **Index Computation** — population-adjusted intensity mapped to 0–100 via frozen baseline CDF
6. **Forecasting** — ETS, LightGBM, state-space ensemble with conformal calibration
7. **Gap Analysis** — demand vs supply with probabilistic shortage/saturation detection
8. **Early Warning** — state machine with hysteresis, templated explainability

*Equations and implementation details: see M2.*
