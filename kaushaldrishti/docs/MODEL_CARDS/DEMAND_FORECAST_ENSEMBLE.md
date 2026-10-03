# Model Card: KaushalDrishti Demand Forecast Ensemble

## 1. Model Details
- **Model Name:** Demand Forecast Ensemble (Layer 6)
- **Version:** 1.0.0
- **Model Architecture:** Multi-model convex ensemble combining Bayesian State-Space projection, Global LightGBM gradient boosted panel regression, Holt-Winters Exponential Smoothing (ETS), and Seasonal Naive (lag-12).
- **Inference Latency:** < 50ms per district-trade cell query; batch evaluation of 5,760 cells in < 30 seconds.
- **Output:** Point forecast of expected monthly openings ($\hat{V}_{t+h}$), 80% credible bounds ($q_{10}, q_{90}$), 95% bounds, and effective sampling variance $\sigma_h = (q_{90} - q_{10}) / (2 \times 1.2816)$.

## 2. Intended Use
- **Primary Domain:** Labour market intelligence for vocational training seat planning, capacity allocation, and early shortage warning under Ministry of Skill Development and Entrepreneurship (MSDE).
- **Horizons:** 3-month, 6-month, 12-month forward projections, and cohort-aligned horizons ($h = L$ where $L$ is course duration in months).
- **Advisory Nature:** strictly advisory; system does not trigger automatic seat closures or sanctions. All human administrative overrides are audited.

## 3. Training & Validation Data
- **Panel Scope:** 3 Pilot States (Karnataka, Tamil Nadu, Uttar Pradesh), 144 districts, 5 priority sectors, 40 priority trades.
- **Time Horizon:** 48 monthly periods (2021-01 to 2024-12).
- **Data Mode:** Explicitly marked `synthetic` with honest labelling across all records and exports.
- **Features:** Lagged log-openings (lags 1, 2, 3, 6, 12), rolling statistics (3m, 6m, 12m), growth rates, cyclical month encoding ($\sin, \cos$), employer breadth ($B$), recency ($R$), corroboration ($I$), and training pipeline capacity.

## 4. Evaluation & Backtest Performance
- **Validation Scheme:** Rolling-origin cross-validation with holdout cutoff months ($T = 2023\text{-}06, 2023\text{-}12$).
- **Metrics Summary:**
  - **Horizon 3m:** MAE 40.2, RMSE 82.2, MAPE 9.5%, 80% Coverage: ~82%, 95% Coverage: ~96%.
  - **Horizon 6m:** MAE 39.6, RMSE 107.1, MAPE 9.2%, 80% Coverage: ~81%, 95% Coverage: ~96%.
  - **Horizon 12m:** MAE 51.0, RMSE 146.2, MAPE 11.4%, 80% Coverage: ~78%, 95% Coverage: ~95%.
- **Uncertainty Calibration:** Split-Conformal Inference scaled by local volatility guarantees distribution-free finite-sample coverage validity.

## 5. Ethical Considerations & Limitations
- **Synthetic Data Caveat:** Current evaluation runs on calibrated synthetic data designed to mimic real-world administrative and portal characteristics. Must be recalibrated when live MoLE/NCS feeds are plugged in.
- **Sparse Cell Fallback:** In sparse cells with insufficient observations, forecasts gracefully fall back to state-level empirical aggregates with explicit `fallback_level >= 1` flags.
- **Exclusion of Placement Data:** Placement data is structurally excluded from demand and supply modeling to eliminate circular incentives and phantom job-matching distortion.
