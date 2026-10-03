# Model Card: Global LightGBM Demand Forecaster

## 1. Model Details
- **Model Name:** Global LightGBM Forecaster (Layer 6)
- **Model Architecture:** Gradient Boosted Decision Trees (LightGBM `LGBMRegressor` with HistGradientBoosting fallback).
- **Hyperparameters:** `n_estimators=120`, `learning_rate=0.06`, `num_leaves=31`, `subsample=0.8`, `colsample_bytree=0.8`.
- **Target:** Direct multi-step projection of log-openings $\ln(V_{t+h} + 1)$ for horizons $h \in \{3, 6, 12\}$.

## 2. Intended Use
- Captures nonlinear cross-sectional interactions across trades, sectors, and geographies.
- Incorporates macroeconomic signals, breadth of hiring employers ($B$), recency index ($R$), and training pipeline capacity.

## 3. Inputs & Features
- **Lagged log-openings:** $lag_1, lag_2, lag_3, lag_6, lag_{12}$.
- **Rolling Statistics:** 3-month, 6-month, 12-month rolling mean and 6-month rolling standard deviation.
- **Growth Dynamics:** 3-month annualized growth, 12-month annual growth.
- **Seasonality:** Month of year cyclical features ($\sin(2\pi m/12), \cos(2\pi m/12)$).
- **Categoricals:** `district_id`, `trade_id`.
- **Supply Pipeline Features:** Past enrolled trainees and allocated training capacity.

## 4. Evaluation Performance
- **MAE:** 25.68 (3m), 27.12 (6m), 26.96 (12m).
- **MAPE:** 6.0% - 6.2% across horizons.
- **Coverage (80% interval):** 81.7% - 85.5% (consistently within target $\pm 5\%$).

## 5. Limitations
- Point forecasts from tree models do not extrapolate beyond historical domain bounds without state-space damping.
- Relies on ensemble weighting with Bayesian State-Space to prevent overconfidence in regime changes.
