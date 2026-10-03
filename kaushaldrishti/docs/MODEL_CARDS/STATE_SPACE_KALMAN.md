# Model Card: Bayesian State-Space Demand Forecaster

## 1. Model Details
- **Model Name:** Bayesian State-Space Filter & Forecaster (Layer 4 & Layer 6)
- **Model Architecture:** Linear-Gaussian State-Space model projecting latent mean $m_t$, trend drift $b_t$, and estimation error covariance $P_t$.
- **Equations:**
  $$m_{t+h} = m_t + \sum_{i=1}^h \phi^i b_t$$
  $$P_{t+h} = P_t + h \cdot Q_\theta$$
  $$\hat{V}_{t+h} = \exp\left(m_{t+h} + \frac{1}{2} P_{t+h}\right)$$
  $$\sigma_h = \sqrt{P_{t+h}}$$
  $$q_{10} = \exp\left(m_{t+h} - 1.2816 \sigma_h\right), \quad q_{90} = \exp\left(m_{t+h} + 1.2816 \sigma_h\right)$$

## 2. Intended Use
- Provides structurally grounded long-term forecasting without empirical overfitting.
- Inherently models expanding uncertainty as horizon $h$ increases via process noise $Q_\theta$.
- Projects cohort-aligned horizons ($h = L$) for course durations between 3 and 12+ months.

## 3. Inputs
- Latent state estimated via Kalman measurement update fusing gated job portal postings, apprentice portals, e-Shram registrations, and PLFS aggregates.
- Damping factor $\phi = 0.95$ ensuring economic stability of projected trends.
- Process noise variance $Q_\theta = 0.04$.

## 4. Strengths & Limitations
- **Strengths:** Mathematically sound uncertainty growth; guaranteed positive projections via log-normal transform; transparent closed-form computation.
- **Limitations:** Does not incorporate non-linear high-dimensional exogenous predictors (handled by ensembling with LightGBM).
