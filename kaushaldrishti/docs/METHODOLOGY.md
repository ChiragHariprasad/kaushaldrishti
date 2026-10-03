# KaushalDrishti: Documented Methodology & Mathematical Specification

**AI-enabled Labour Market Intelligence System (LMIS)**
Ministry of Skill Development & Entrepreneurship (MSDE) | SIH 2026 (SIH26246)

---

## 1. Overview & Core Mathematical Principles

KaushalDrishti estimates latent district-level labour demand through a multi-source Bayesian state-space information filter. Rather than relying on a single raw portal feed or unverified scraping, the system fuses complementary signals (public aggregates, government vacancy registries, private portal postings, enterprise registrations) with explicit bias modeling, reliability gating, and empirical Bayes shrinkage.

To ensure comparability between major industrial metropolitan districts (e.g. Bengaluru Urban) and rural or aspirational districts (e.g. Yadgir), the system evaluates:
1. **Absolute log-openings scale** ($m, P$) for cohort-window gap analysis and seat target modeling.
2. **Demand intensity per 100,000 working-age population** ($\iota$) mapped to a percentile **Labour Demand Index ($LDI \in [0, 100]$)** against a frozen historical baseline.

---

## 2. Layer 3: Evidence Unit Construction

For each data source $k$, month $t$, and district-trade cell $(s, d, t)$:

### 2.1 Effective Volume
$$n_{eff} = \sum_{i \in \text{cell}} m_i$$
where $m_i \in [0, 1]$ is the calibrated taxonomy match confidence of de-duplicated posting $i$.

### 2.2 Coverage and Seasonality Correction
$$\hat{o} = \frac{n_{eff}}{\text{seasonal\_factor}_{k, State, \text{broad\_sector}, month} \times \text{coverage}_{k, State, \text{broad\_sector}}}$$

- **Seasonal factors** are estimated via STL decomposition at the State level to prevent noisy estimates in sparse districts.
- **Coverage ratios** are estimated against payroll/PLFS-derived State $\times$ broad-sector anchors over an overlap window, shrunk toward the national ratio. Corrections are applied strictly at the State $\times$ broad-sector level, never forced at occupation level.

### 2.3 Log Transformation & Variance Estimation
$$y = \ln(\hat{o} + 0.5)$$
$$\sigma^2 = \frac{1}{n_{eff} + 1} + \sigma^2_{\text{cov}, k} + \sigma^2_{\text{dup}, k}$$

where $\sigma^2_{\text{cov}, k}$ accounts for sampling coverage error and $\sigma^2_{\text{dup}, k}$ models duplicate/ghost inflation variance.

### 2.4 Calibration to Anchor Scale
$$y = \alpha_k + \beta_k \cdot \theta + \varepsilon, \quad \beta_k \sim N(1, 0.1^2)$$
The calibrated observation and observation variance are:
$$z = \frac{y - \alpha_k}{\beta_k}$$
$$v = \frac{\sigma^2}{r_k \cdot \beta_k^2}$$
where $r_k \in [0.1, 1.0]$ is the dynamic source reliability factor.

---

## 3. Layer 4: Reliability Gate & Source Factor ($r_k$)

An incoming source observation passes the reliability gate for cell $(s, d, t)$ if and only if all four conditions hold:

1. **Coverage**: $n_{eff} \ge 10$ over trailing 90 days.
2. **Freshness**: $\text{age} \le 2 \times \text{nominal\_update\_days}_k$.
3. **Stability**: Rolling 6-month Median Absolute Deviation (MAD) of standardised residuals $\le 2.5$.
4. **Consensus Agreement**:
   $$\frac{|z - m_{(-k)}|}{\sqrt{v + P_{(-k)}}} \le 3.0$$
   in at least 4 of the last 6 months, where $m_{(-k)}, P_{(-k)}$ is the leave-one-out consensus.

Failing sources contribute zero weight ($w_k = 0$, $\text{contribution}_k = 0$), and the failure reason is recorded in `gate_reason`.

### 3.1 Dynamic Reliability Factor ($r_k$)
$$r_k = \text{clip}\left(\frac{\bar{v}_k}{\text{MSE}_k}, 0.1, 1.0\right)$$
where $\text{MSE}_k$ is the rolling mean of excess squared leave-one-out deviations, floored at nominal observation variance $\bar{v}_k$.

---

## 4. Layer 4: Kalman Fusion in Information Form

### 4.1 State Equations
$$\theta_t = \theta_{t-1} + b_{t-1} + \eta_t, \quad \eta_t \sim N(0, Q_\theta)$$
$$b_t = \phi \cdot b_{t-1} + \zeta_t, \quad \zeta_t \sim N(0, Q_b), \quad \phi = 0.9$$

### 4.2 Prior Prediction Step
$$m_{t|t-1} = m_{t-1} + b_{t-1}$$
$$P_{t|t-1} = P_{t-1} + Q_\theta$$

### 4.3 Information-Form Measurement Update
$$P_t^{-1} = P_{t|t-1}^{-1} + \sum_{k \in \text{gated}} v_k^{-1}$$
$$m_t = P_t \left( P_{t|t-1}^{-1} m_{t|t-1} + \sum_{k \in \text{gated}} \frac{z_k}{v_k} \right)$$
Missing or ungated sources add no term (no imputation).

### 4.4 Exact Source Attribution (Why Panel)
The weight of source $k$ is:
$$w_k = \frac{v_k^{-1}}{P_t^{-1}}$$
The contribution of source $k$ to the change in level is:
$$\text{contribution}_k = w_k \cdot (z_k - m_{t|t-1})$$
The prior state retains weight:
$$w_{\text{prior}} = \frac{P_{t|t-1}^{-1}}{P_t^{-1}}$$
$$\sum_{k \in \text{gated}} w_k + w_{\text{prior}} \equiv 1.0, \quad m_t - m_{t|t-1} \equiv \sum_{k \in \text{gated}} \text{contribution}_k$$

---

## 5. Partial Pooling & Empirical Bayes Shrinkage

To borrow statistical strength from State-level trends for small or sparse districts:

$$\delta_d \sim N(0, \tau_s^2)$$
$$\tau_s^2 = \max\left(0.001, \text{Var}_d(m) - \text{mean}(P)\right)$$

The shrinkage parameter $\lambda$ and data share $\omega$ are:
$$\lambda = \frac{\tau_s^{-2}}{\tau_s^{-2} + P_{\text{data}}^{-1}}, \quad \omega = 1 - \lambda$$
$$m_{\text{pooled}} = (1 - \lambda) m_{\text{district}} + \lambda m_{\text{state}}$$
$$P_{\text{pooled}}^{-1} = P_{\text{data}}^{-1} + \tau_s^{-2}$$

If a district has no admissible data, the pipeline gracefully falls back to State level (`fallback_level: 1`) or National level (`fallback_level: 2`).

---

## 6. Labour Demand Index (LDI) & Frozen Baseline

### 6.1 Population-Standardized Intensity ($\iota$)
$$\iota = m - \ln\left(\frac{\text{pop\_working\_age}_d}{100,000}\right)$$

### 6.2 Mapping via Frozen Baseline Empirical CDF ($F_{\text{ref}, s}$)
$$LDI = 100 \times F_{\text{ref}, s}(\iota)$$
- Baseline intensities are frozen over the first 24-month reference period (2021-01 to 2022-12) and committed to `config/baseline.json`. Re-basing is an audited, deliberate act.
- 80% credible bounds:
  $$\iota_{\text{lo}} = \iota - 1.2816 \sqrt{P}, \quad \iota_{\text{hi}} = \iota + 1.2816 \sqrt{P}$$
  $$LDI_{\text{lo}} = 100 \times F_{\text{ref}, s}(\iota_{\text{lo}}), \quad LDI_{\text{hi}} = 100 \times F_{\text{ref}, s}(\iota_{\text{hi}})$$

---

## 7. Driver Descriptors

Alongside the posterior index, six descriptors describe the underlying dynamics:

1. **Volume ($V$)**: Expected openings $V = \exp(m)$.
2. **Growth ($G$)**: 3-month annualized log slope $G = (m_t - m_{t-3}) \times 400\%$.
3. **Recency ($R$)**: Time-decayed source freshness index $R = \sum_k w_k \exp(-\text{age}_k / 30)$.
4. **Growth Persistence ($P_{\text{persist}}$)**: Consecutive months with unchanged growth sign (capped at 12).
5. **Breadth ($B$)**: Effective employer diversity (inverse Herfindahl index) $B = 1 / \sum s_i^2$.
6. **Corroboration ($I$)**: Proportion of independent source groups agreeing in growth direction ($I \in [0, 1]$).

---

## 8. Confidence Badge Assignment

| Confidence | Uncertainty ($\sqrt{P}$) | Local Data Share ($\omega$) | Independent Sources | Fallback Level |
|------------|--------------------------|-----------------------------|---------------------|----------------|
| **High**   | $\le 0.35$               | $\ge 65\%$                  | $\ge 3$             | Level 0 (District) |
| **Medium** | $\le 0.65$               | $\ge 35\%$                  | $\ge 2$             | $\le 1$ (State fallback allowed) |
| **Low**    | $> 0.65$                 | $< 35\%$                    | $< 2$               | Any |
