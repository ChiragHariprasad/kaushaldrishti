# Model Card: Benchmark Baselines (ETS & Seasonal Naive)

## 1. Model Details
- **Models:**
  1. **Seasonal Naive:** Projections equal observations from the same season last year ($\hat{y}_{t+h} = y_{t+h-12}$). Uncertainty expands as $\sigma \sqrt{\lceil h / 12 \rceil}$.
  2. **Holt-Winters ETS:** Triple exponential smoothing with additive level ($\alpha=0.3$), additive trend ($\beta=0.1$), and additive seasonality ($\gamma=0.2$, period $s=12$).

## 2. Intended Use
- Industry-standard benchmarks serving as reference baselines in rolling-origin cross-validation.
- Included as low-weight stabilization anchors (10-15%) in the multi-model ensemble to prevent catastrophic failure on atypical series.

## 3. Backtest Metrics
- **Seasonal Naive:** MAE 41.4 - 48.1, MAPE 7.9% - 8.6%, 80% Coverage: 76.2% - 81.7%.
- **SimpleETS:** MAE 43.0 - 45.4, MAPE 9.0% - 9.4%, 80% Coverage: 87.3% - 95.5%.
