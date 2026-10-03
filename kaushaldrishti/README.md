# KaushalDrishti

**AI-enabled Labour Market Intelligence System (LMIS)**
Ministry of Skill Development and Entrepreneurship (MSDE)
Smart India Hackathon 2026 — Problem Statement SIH26246

---

## Overview

KaushalDrishti is a forecasting dashboard that provides district-level labour demand intelligence for **3 pilot States** (Karnataka, Tamil Nadu, Uttar Pradesh) across **5 sectors** (Construction, Electronics & Hardware, Healthcare, Automotive, Logistics & Supply Chain). It features:

- **Demand Index (LDI)**: Kalman-fused, multi-source demand intensity index (0–100)
- **Supply Forecasting**: Beta-posterior pipeline modelling (capacity → enrollment → completion → certification)
- **Gap Analysis & Early Warning**: Probabilistic shortage/saturation detection with hysteresis
- **Policy Scenario Simulator**: What-if analysis for seat allocation changes
- **Multilingual Interface**: English, Hindi, Kannada, Tamil (WCAG 2.2 AA compliant)

## Quick Start

```bash
# Clone and start everything
make demo

# Run tests
make test

# Refresh data pipeline
make refresh

# Run backtests
make backtest

# Export data
make export
```

## Golden Path (3 clicks)

1. **National Overview** → click Karnataka
2. **State Explorer** → click a district → Automotive sector
3. **Trade View** → EV Service Technician → see LDI, forecast, gap, status
4. Click **Why** → see source contributions
5. Open **Scenario Lab** → raise seats +15% → see gap path
6. **Export CSV**

## Data Drop-in

Place files in `data/incoming/`:
- PLFS tables (State-level employment)
- NCS vacancy extracts
- e-Shram district aggregates
- NCO-2015 code list
- QP-to-NCO mapping

See `docs/DATA_SOURCES.md` for details. If files are absent, synthetic data is generated and clearly labelled.

## Architecture

See `docs/METHODOLOGY.md` for the full demand-index methodology with equations.

## Known Limitations

- Synthetic cells are labelled `data_mode: synthetic` — never presented as real data
- Vacancies are not hires; the index measures demand signals, not actual employment
- Thresholds are defaults tuned on available data
- Synthetic validation proves the pipeline works, not real-world accuracy
- All NCO codes are `verified: false` unless from an official supplied file

## License

Built for SIH 2026. All rights reserved.
