# KaushalDrishti (कौशलदृष्टि)

**AI-Enabled Labour Market Intelligence System (LMIS)**  
*Ministry of Skill Development & Entrepreneurship (MSDE), Government of India*  
**Smart India Hackathon 2026 — Problem Statement SIH26246**

---

## 1. Executive Summary

**KaushalDrishti** is an operational, auditable Labour Market Intelligence System designed for district-level skill planning across India. Built for the Ministry of Skill Development and Entrepreneurship (MSDE), it models labour market supply-demand dynamics across **3 pilot States** (Karnataka, Tamil Nadu, Uttar Pradesh; 144 districts), **5 priority sectors** (Automotive, Capital Goods, Electronics, Healthcare, IT-ITeS), and **40 priority trades** across a **48-month longitudinal panel**.

The platform is designed around strict government operational realities: **honesty over polish**, **deterministic runtime serving** (zero LLMs in the runtime inference path), **mathematical rigor** (closed-form Kalman information fusion, split-conformal prediction intervals, stock-flow cohort lag models), and **multilingual accessibility** (English, Hindi, Kannada, Tamil).

---

## 2. Core Architectural Pillars & Invariants

| # | Invariant | Technical Implementation | Why It Matters |
|---|---|---|---|
| 1 | **Per-Cell Honest Labelling** | Every cell carries immutable `data_mode`: `live`, `public_aggregate`, `partner`, or `synthetic`. | Organizers supply dummy data; honest badges protect credibility and prevent misrepresenting synthetic data. |
| 2 | **Closed-Form Kalman Fusion** | Information filter: $Y_t = \sum r_k H_k^T R_k^{-1} y_k$, $M_t = \sum r_k H_k^T R_k^{-1} H_k$, $\hat{x}_t = M_t^{-1} Y_t$. | Sub-10ms deterministic response with exact percentage attribution per feed source without MCMC inference lag. |
| 3 | **Supply Pipeline Invariant** | $S_{\text{cert}} = C \times E \times CR \times Cert$. Placement outcomes are **structurally excluded**. | Prevents circularity and false supply suppression. Employed graduates cannot be counted as open available supply. |
| 4 | **Conformal Uncertainty** | Split-conformal calibration with horizon volatility scaling: $\sigma_h = (q_{90} - q_{10}) / (2 \times 1.2816)$. | Distribution-free coverage guarantee. Empirical 80% coverage: 81.7% at 6m, 79.3% at 12m ($\pm 5\%$ tolerance). |
| 5 | **Hysteresis State Machine** | 2 consecutive refreshes required to escalate; de-escalation requires probability margin $(\text{threshold} - 0.10)$. | Eliminates false alarm chatter and oscillation at decision boundaries. Shortage and Saturation are mutually exclusive. |
| 6 | **Stock-Flow Policy Simulator** | $S(t) = \sum C_c' E_c (CR_c + \Delta CR) Cert_c \cdot \mathbb{I}[t_c + L = t]$. | Enforces cohort training delay $L$ and facility commissioning lag. Prohibits unrealistic instantaneous supply creation. |
| 7 | **Official Taxonomy Compliance** | Indicative mappings marked `verified: false`. Exact Levenshtein distance for LGD district resolution. | Respects official NCO-2015 codes and Census/LGD directory standards. |

---

## 3. Official Evaluation Golden Path (≤ 3 Clicks Per Level)

To evaluate the complete end-to-end decision workflow during hackathon judging:

```
[1. National Overview] ──> [2. Karnataka State] ──> [3. Bengaluru Urban]
                                                              │
[6. Policy Scenario Lab] <── [5. "Why" Attribution] <── [4. EV Service Technician]
         │
         ▼
[7. Export Validated CSV]
```

1. **National Overview**: Open dashboard at `http://localhost:80`. Observe national KPI cards, state-by-state comparisons (KA, TN, UP), and top acute shortages. Click **Karnataka**.
2. **State & District Explorer**: Select **Bengaluru Urban** (LGD: 556). Filter by **Automotive** sector.
3. **Forecast Centre**: Select **EV Service Technician** (QP: `ASC/Q1402`, NCO: `7231.0101 [verified: false]`, NSQF 4).
   - Observe LDI Gauge: `72.4` [68.1, 76.8]
   - Observe Forecast Demand ($E[D]=198$) vs Certified Supply ($S_W=162$). Net Gap: `+36` ($p_S = 84\%$, Severity = `40.0`, Flag: `Acute Shortage`).
   - Switch horizons: `3m`, `6m`, `12m`, `Cohort L (12m)`. Inspect multi-series chart with conformal 80% and 95% uncertainty bands.
4. **"Why" Attribution Modal**: Click **Explain Why**. Inspect exact information weights:
   - National Career Service (NCS): `42.1%`
   - Karnataka Kaushalkar Portal: `31.8%`
   - Apprenticeship Portal (NAPS): `17.5%`
   - PLFS & e-Shram Priors: `8.6%`
   - Review 6 driver descriptors ($V, G, R, P_{persist}, B, I$) and deterministic multilingual explanation narrative.
5. **Policy Scenario Lab**: Click **Test in Scenario Lab**.
   - Set **Seat Allocation Delta** to `+15%` (default).
   - Inspect **"GAP CLOSES IN CYCLE"** callout: Target deficit extinguished in **Cycle 2 (Month 18)** with +34 certified grads/year.
   - Verify stock-flow lag: Month 1–11 supply remains flat due to $L=12$m cohort delay; gap closes once expansion cohort matures.
6. **Executive District Brief**: Click **Print District Brief** in header to review the 1-page printable MSDE executive summary.
7. **Export Data**: Click **Export CSV** to download the auditable multi-district panel dataset.

---

## 4. Quick Start & Commands

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (optional for full containerized stack)

### 1-Command Full Stack Demo
```bash
# Start Docker stack (FastAPI backend + Next.js frontend + Nginx reverse proxy)
make demo
```
- Dashboard: [http://localhost:80](http://localhost:80)
- API Service: [http://localhost:8000](http://localhost:8000)
- Interactive OpenAPI Docs: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)

### Verification & Testing
```bash
# Run full backend unit and contract tests (47 tests)
make test

# Run rolling-origin backtests across 48-month panel
make backtest

# Export data in all 5 formats (CSV, XLSX, JSON, GeoJSON, Parquet)
make export

# Type-check and lint frontend and backend
make lint
```

---

## 5. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Next.js 16 Responsive UI                           │
│  [National Overview]  [District Explorer]  [Forecast Centre]            │
│  [Early Warning Reg]  [Scenario Lab]       [Methodology & Validation]   │
│  (Multilingual: en, hi, kn, ta • WCAG 2.2 AA • Low-Bandwidth Mode)      │
└────────────────────────────────────▲────────────────────────────────────┘
                                     │ REST APIs & Webhooks
┌────────────────────────────────────▼────────────────────────────────────┐
│                       FastAPI Backend Engine                            │
│  ├─ /api/v1/health & /api/v1/quality (Gate Monitoring)                  │
│  ├─ /api/v1/demand-index & /api/v1/explain (Kalman Information Fusion) │
│  ├─ /api/v1/supply-forecasts (Beta-Posterior Pipeline)                 │
│  ├─ /api/v1/forecasts & /api/v1/validation (Conformal Calibrated)      │
│  ├─ /api/v1/gaps & /api/v1/alerts (Hysteresis State Machine)           │
│  ├─ /api/v1/scenarios (Stock-Flow Delay Policy Simulator)              │
│  ├─ /api/v1/lineage/{cell_id} (Data Provenance & Audit Trail)          │
│  └─ /api/v1/export (CSV, XLSX, JSON, GeoJSON, Parquet)                 │
└────────────────────────────────────▲────────────────────────────────────┘
                                     │
┌────────────────────────────────────┴────────────────────────────────────┐
│                       Data & Modelling Engine                           │
│  ├─ Geo Resolver: LGD codes, fuzzy Levenshtein, alias mapping           │
│  ├─ Ingest Adapters: PLFS, NCS, e-Shram, State Portals, NAPS            │
│  ├─ Conformal Calibrator: Volatility-scaled non-parametric bands        │
│  ├─ Forecast Ensemble: Min-Pinball ETS + Kalman + LightGBM              │
│  └─ Data Store: SQLite/PostGIS + Columnar Parquet Backing Store         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Empirical Validation & Backtest Results

From 31,680 sliding-window backtests on the 48-month longitudinal panel (`docs/BACKTESTS.md`):

| Horizon | Nominal Coverage Target | Empirical Coverage | WAPE | Pinball Loss | Status |
|---|---|---|---|---|---|
| **3 Months** | 80.0% | **87.3%** | 11.2% | 4.82 | **Passed** |
| **6 Months** | 80.0% | **81.7%** | 14.6% | 6.21 | **Passed** |
| **12 Months** | 80.0% | **79.3%** | 18.4% | 8.44 | **Passed** |

### Planted Episode Proofs (`planted.json`)
The synthetic generator embeds 30 real-world shock patterns (10 acute shortages, 10 demand surges, 10 supply dropouts). The early warning pipeline achieves:
- **Detection Recall**: **100.0%** (Target: $\ge 80\%$)
- **Brier Probability Score**: **0.12** (Target: $\le 0.25$)
- **Mean Detection Lead Time**: **1.2 months** (Target: $\le 2$ months)
- **False Discovery Rate**: **6.7%** (Target: $\le 15\%$)

---

## 7. Project Layout

```
kaushaldrishti/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # 20 FastAPI endpoints (demand, supply, gap, scenario, export, lineage, webhooks)
│   │   ├── core/                # Configuration, security, logging
│   │   └── db/                  # SQLAlchemy models and SQLite/PostGIS database session
│   ├── pipelines/
│   │   ├── taxonomy/            # NCO/QP normalizer, fuzzy matcher, LGD geo resolver
│   │   ├── ingest/              # Adapters (PLFS, NCS, e-Shram, State, Apprenticeship) & quality gate
│   │   ├── demand/              # Closed-form Kalman information filter & empirical Bayes partial pooling
│   │   ├── supply/              # Beta-Binomial posterior pipeline models
│   │   ├── forecast/            # ETS, Kalman state-space, LightGBM, Conformal calibrator, Min-Pinball ensemble
│   │   ├── gap/                 # Hysteresis state machine, multilingual explainer, alert engine
│   │   └── scenario/            # Stock-flow cohort delay policy simulator
│   ├── scripts/                 # Seeding, backtesting, export runners
│   └── tests/                   # 47 unit & contract tests across 10 test modules
├── frontend/
│   ├── app/
│   │   ├── components/          # Navbar, NationalOverview, DistrictExplorer, ForecastCentre, EarlyWarningCentre,
│   │   │                        # ScenarioLab, MethodologyValidation, WhyPanel, DistrictBriefModal
│   │   ├── i18n.ts              # Multilingual translations (en, hi, kn, ta)
│   │   ├── page.tsx             # Main dashboard with Golden Path navigation
│   │   └── layout.tsx           # MSDE root layout
│   └── package.json
├── data/
│   ├── incoming/                # Raw data drop-in folder
│   ├── synthetic/               # Generated 48-month panel parquets and planted episodes
│   ├── exports/                 # Generated exports (CSV, XLSX, JSON, GeoJSON, Parquet)
│   └── seeds/                   # Taxonomy, state, district, and sector seeds
├── docs/
│   ├── BACKTESTS.md             # Detailed backtest calibration logs
│   ├── DECISIONS.md             # 38 Architectural Decision Records (D-001 to D-038)
│   ├── openapi.json             # Full OpenAPI 3.1.0 specification
│   └── MODEL_CARDS/             # Formal model cards for forecasting architectures
├── docker-compose.yml           # Full-stack orchestrator
└── Makefile                     # Developer & judge command targets
```

---

## 8. License & Attribution

Developed for the **Smart India Hackathon (SIH) 2026**.  
Ministry of Skill Development & Entrepreneurship (MSDE), Government of India.  
*Honest, Auditable, Multilingual Labour Market Intelligence.*
