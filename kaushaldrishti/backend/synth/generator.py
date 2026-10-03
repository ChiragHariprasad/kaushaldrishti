"""
Synthetic Data Generator with Planted Episodes for KaushalDrishti.
Deterministic generation across 144 districts x 40 trades x 48 months.
Generates:
- Latent demand truth & multi-source evidence
- Training supply pipeline
- 15 shortage + 15 saturation planted episodes
- Parquet outputs in data/synthetic/ with data_mode='synthetic'
"""

import json
import math
import os
import random
from datetime import datetime
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd


RANDOM_SEED = 42
MONTHS_HISTORY = 48
START_YEAR = 2021
START_MONTH = 1


def get_month_str(offset: int) -> str:
    """Generates YYYY-MM from month offset starting 2021-01."""
    y = START_YEAR + (START_MONTH - 1 + offset) // 12
    m = (START_MONTH - 1 + offset) % 12 + 1
    return f"{y:04d}-{m:02d}"


MONTHS = [get_month_str(i) for i in range(MONTHS_HISTORY)]


def generate_planted_episodes() -> List[Dict[str, Any]]:
    """
    Creates 15 shortage and 15 saturation planted episodes with ground truth onset months.
    Stored in synth/planted.json for pipeline validation.
    """
    episodes = []

    # 15 Shortage Episodes (rapidly rising demand, lagging training capacity)
    shortage_configs = [
        ("Karnataka", "Bengaluru Urban", "EV Service Technician", 18, 12, "Surge in EV two-wheeler deliveries & charging infra"),
        ("Karnataka", "Mysuru", "EV Service Technician", 24, 10, "Expansion of EV fleet hubs in tier-2 city"),
        ("Karnataka", "Dharwad", "Solar Panel Installation Technician", 20, 8, "Rooftop solar PM Surya Ghar adoption"),
        ("Karnataka", "Dakshina Kannada", "General Duty Assistant", 15, 14, "Hospital network expansion"),
        ("Karnataka", "Tumakuru", "Warehouse Associate", 28, 9, "New warehousing corridor"),

        ("Tamil Nadu", "Chennai", "EV Service Technician", 16, 14, "Automotive cluster transition to EV powertrains"),
        ("Tamil Nadu", "Coimbatore", "CNC Machining Technician", 22, 10, "Precision engineering export demand surge"),
        ("Tamil Nadu", "Tiruppur", "Industrial Sewing Machine Operator", 18, 12, "Apparel export order surge"),
        ("Tamil Nadu", "Salem", "Electrician (Construction)", 25, 9, "Industrial park electrification project"),
        ("Tamil Nadu", "Chengalpattu", "CCTV Installation Technician", 30, 8, "Electronics manufacturing corridor expansion"),

        ("Uttar Pradesh", "Gautam Buddha Nagar", "Mobile Phone Repair Technician", 14, 16, "Mobile handset assembly and after-sales boom"),
        ("Uttar Pradesh", "Lucknow", "Emergency Medical Technician", 22, 12, "State emergency ambulance service expansion"),
        ("Uttar Pradesh", "Varanasi", "Warehouse Associate", 26, 10, "Multi-modal logistics park launch"),
        ("Uttar Pradesh", "Agra", "Solar Panel Installation Technician", 24, 12, "Solarization drive across hospitality sector"),
        ("Uttar Pradesh", "Kanpur Nagar", "Last-Mile Delivery Executive", 20, 14, "E-commerce expansion in central UP"),
    ]

    for state, dist, trade, onset_idx, dur, desc in shortage_configs:
        episodes.append({
            "episode_id": f"SHORT_{len(episodes)+1:02d}",
            "type": "shortage",
            "state": state,
            "district": dist,
            "trade": trade,
            "onset_month_idx": onset_idx,
            "onset_month": MONTHS[onset_idx],
            "duration_months": dur,
            "description": desc,
            "demand_multiplier": 2.2,
            "supply_multiplier": 0.7,
        })

    # 15 Saturation Episodes (collapsing demand or over-trained supply cohorts)
    saturation_configs = [
        ("Karnataka", "Bengaluru Urban", "Vehicle Painter", 20, 12, "Automated painting bays in major body shops"),
        ("Karnataka", "Belagavi", "Two Wheeler Service Technician", 24, 10, "Market saturation from excessive local batches"),
        ("Karnataka", "Kalaburagi", "Wireman", 18, 14, "Surplus local certified wiremen pool"),
        ("Karnataka", "Shivamogga", "Plumber (General)", 22, 12, "Residential construction slowdown"),
        ("Karnataka", "Ballari", "Bar Bender & Steel Fixer", 26, 10, "Commercial real-estate pause"),

        ("Tamil Nadu", "Chennai", "Freight Handler", 16, 14, "Automated conveyor handling at container freight stations"),
        ("Tamil Nadu", "Madurai", "Domestic Wireman", 22, 10, "Oversupply of basic domestic electrical certificate holders"),
        ("Tamil Nadu", "Tirunelveli", "Mason (General)", 20, 12, "Prefabricated building adoption"),
        ("Tamil Nadu", "Erode", "Auto Electrician", 24, 10, "Legacy 12V automotive wiring decline"),
        ("Tamil Nadu", "Vellore", "General Duty Assistant", 28, 8, "Excess certified GDA batches without hospital tie-ups"),

        ("Uttar Pradesh", "Ghaziabad", "Last-Mile Delivery Executive", 24, 12, "Rider oversupply and platform consolidation"),
        ("Uttar Pradesh", "Meerut", "Welder (Arc & Gas)", 20, 14, "Steel fabrication shop automation"),
        ("Uttar Pradesh", "Aligarh", "Electronics Mechanic", 26, 10, "Decline in component-level PCB repair"),
        ("Uttar Pradesh", "Bareilly", "Scaffolder", 22, 12, "Local infrastructure project completion"),
        ("Uttar Pradesh", "Prayagraj", "Phlebotomist", 18, 14, "Diagnostic chain diagnostic centralization"),
    ]

    for state, dist, trade, onset_idx, dur, desc in saturation_configs:
        episodes.append({
            "episode_id": f"SATUR_{len(episodes)+1:02d}",
            "type": "saturation",
            "state": state,
            "district": dist,
            "trade": trade,
            "onset_month_idx": onset_idx,
            "onset_month": MONTHS[onset_idx],
            "duration_months": dur,
            "description": desc,
            "demand_multiplier": 0.45,
            "supply_multiplier": 1.9,
        })

    return episodes


def generate_synthetic_dataset(
    output_dir: str,
    districts_csv: str,
    trades_csv: str,
) -> Dict[str, Any]:
    """
    Generates all canonical synthetic tables as Parquet files.
    """
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    os.makedirs(output_dir, exist_ok=True)

    # 1. Load Districts and Trades
    districts_df = pd.read_csv(districts_csv)
    trades_df = pd.read_csv(trades_csv)

    n_districts = len(districts_df)
    n_trades = len(trades_df)
    print(f"[INFO] Generating synthetic data for {n_districts} districts x {n_trades} trades x {MONTHS_HISTORY} months...")

    # 2. Planted Episodes
    planted_episodes = generate_planted_episodes()
    planted_json_path = os.path.join(output_dir, "planted.json")
    with open(planted_json_path, "w", encoding="utf-8") as f:
        json.dump(planted_episodes, f, indent=2)
    print(f"[OK] Saved {len(planted_episodes)} planted episodes to {planted_json_path}")

    # Build lookup map for planted episodes: (district_name, trade_name, month_idx) -> (d_mult, s_mult)
    episode_map = {}
    for ep in planted_episodes:
        d_name = ep["district"]
        t_name = ep["trade"]
        start = ep["onset_month_idx"]
        end = start + ep["duration_months"]
        for m_idx in range(start, min(end, MONTHS_HISTORY)):
            episode_map[(d_name, t_name, m_idx)] = (ep["demand_multiplier"], ep["supply_multiplier"])

    # 3. Base latent rates per trade
    # Baseline log-intensity per 100k working-age population
    trade_base_log_rate = {}
    for _, t in trades_df.iterrows():
        # High demand: EV Tech, Solar, Warehouse, Last Mile, GDA
        t_name = t["trade_name"]
        if "EV Service" in t_name or "Last-Mile" in t_name or "Warehouse" in t_name or "Solar" in t_name:
            trade_base_log_rate[t_name] = np.random.normal(3.8, 0.3)
        elif "Nursing" in t_name or "Electrician" in t_name or "Plumber" in t_name or "CNC" in t_name:
            trade_base_log_rate[t_name] = np.random.normal(3.2, 0.25)
        else:
            trade_base_log_rate[t_name] = np.random.normal(2.6, 0.2)

    # 4. Generate Latent Demand Truth & Multi-Source Observations
    evidence_rows = []
    pipeline_rows = []

    # Source definitions
    sources = ["ncs", "portal", "plfs", "eshram", "udyam"]

    for d_idx, dist in districts_df.iterrows():
        d_name = dist["district_name"]
        s_name = dist["state_name"]
        pop = dist["population_working_age"]
        urban = dist["urban_rural_aspirational"]

        # Pop scale: openings scale with population
        pop_scale = math.log(max(pop, 50000) / 100000.0)

        # Urban multiplier
        urban_boost = 0.3 if urban == "urban" else (-0.2 if urban == "aspirational" else 0.0)

        for t_idx, trade in trades_df.iterrows():
            t_name = trade["trade_name"]
            course_l = int(trade["course_months"])
            trade_id = t_idx + 1
            district_id = d_idx + 1

            # Base level for this cell
            cell_base_log = trade_base_log_rate[t_name] + pop_scale + urban_boost

            # Sector seasonality
            sec = trade["sector_code"]
            season_phase = 0.0 if sec == "CONST" else (1.5 if sec == "LOGIS" else 0.5)

            # Training centre setup for this cell
            # Typical capacity per batch
            n_centres = 3 if urban == "urban" else (1 if urban == "aspirational" else 2)
            base_capacity = n_centres * (40 if course_l <= 3 else 25)

            for m_idx, m_str in enumerate(MONTHS):
                # Monthly seasonality: construction drops in monsoons (m=6,7,8), logistics peaks in festive (m=9,10,11)
                month_of_year = (START_MONTH - 1 + m_idx) % 12 + 1
                seasonal_adj = 0.25 * math.sin(2 * math.pi * (month_of_year + season_phase) / 12.0)

                # Secular trend
                trend = 0.015 * m_idx if "EV Service" in t_name or "Solar" in t_name else 0.003 * m_idx

                # Check planted episode
                planted_d_mult, planted_s_mult = episode_map.get((d_name, t_name, m_idx), (1.0, 1.0))

                # True log openings
                true_log_openings = cell_base_log + seasonal_adj + trend + math.log(planted_d_mult) + np.random.normal(0, 0.08)
                true_openings = max(1.0, math.exp(true_log_openings))

                # ── Generate Evidence Units for each source ──
                # 1. NCS (Government Vacancies)
                # Lag 1 month, coverage ~ 0.35, low dup
                ncs_eff = max(0, int(np.random.poisson(true_openings * 0.35 * (0.8 if m_idx == 0 else 1.0))))
                evidence_rows.append({
                    "month": m_str,
                    "district_id": district_id,
                    "trade_id": trade_id,
                    "source_id": "ncs",
                    "n_eff": float(ncs_eff),
                    "o_hat": float(ncs_eff / 0.35),
                    "y_log": float(np.log(ncs_eff / 0.35 + 0.5)),
                    "sigma2": float(1.0 / (ncs_eff + 1) + 0.05),
                    "alpha": 0.0,
                    "beta": 1.0,
                    "z": float(np.log(ncs_eff / 0.35 + 0.5)),
                    "v": float(1.0 / (ncs_eff + 1) + 0.05),
                    "gate_pass": bool(ncs_eff >= 2 or m_idx >= 3),
                    "gate_reason": None if ncs_eff >= 2 else "coverage_low",
                    "r_k": 0.95,
                    "data_mode": "synthetic",
                })

                # 2. Portal (Private Job Portals)
                # High urban coverage, 20% duplicate inflation
                portal_coverage = 0.65 if urban == "urban" else 0.25
                portal_eff = max(0, int(np.random.poisson(true_openings * portal_coverage * 1.20)))
                evidence_rows.append({
                    "month": m_str,
                    "district_id": district_id,
                    "trade_id": trade_id,
                    "source_id": "portal",
                    "n_eff": float(portal_eff),
                    "o_hat": float(portal_eff / (portal_coverage * 1.20)),
                    "y_log": float(np.log(portal_eff / (portal_coverage * 1.20) + 0.5)),
                    "sigma2": float(1.0 / (portal_eff + 1) + 0.12),  # Higher noise from ghost/dup
                    "alpha": 0.18,  # Positive bias from duplicates
                    "beta": 1.05,
                    "z": float((np.log(portal_eff / (portal_coverage * 1.20) + 0.5) - 0.18) / 1.05),
                    "v": float(1.0 / (portal_eff + 1) + 0.12),
                    "gate_pass": True,
                    "gate_reason": None,
                    "r_k": 0.88,
                    "data_mode": "synthetic",
                })

                # 3. e-Shram (Stock Registrations aggregate)
                eshram_stock = max(10, int(true_openings * 3.5 + np.random.normal(50, 10)))
                evidence_rows.append({
                    "month": m_str,
                    "district_id": district_id,
                    "trade_id": trade_id,
                    "source_id": "eshram",
                    "n_eff": float(eshram_stock),
                    "o_hat": float(eshram_stock / 3.5),
                    "y_log": float(np.log(eshram_stock / 3.5 + 0.5)),
                    "sigma2": 0.15,
                    "alpha": 0.05,
                    "beta": 0.98,
                    "z": float(np.log(eshram_stock / 3.5 + 0.5)),
                    "v": 0.16,
                    "gate_pass": True,
                    "gate_reason": None,
                    "r_k": 0.92,
                    "data_mode": "synthetic",
                })

                # ── Generate Training Supply Pipeline ──
                # Capacity modified by planted episode
                cap = max(10, int(base_capacity * planted_s_mult))
                seats = int(cap * np.random.uniform(0.9, 1.0))
                # Beta draws: Fill rate E ~ Beta(18, 2), CR ~ Beta(16, 4), Cert ~ Beta(17, 3)
                fill_rate = np.random.beta(18, 2)
                cr_rate = np.random.beta(16, 4)
                cert_rate = np.random.beta(17, 3)

                enrolled = max(5, int(seats * fill_rate))
                completed = max(3, int(enrolled * cr_rate))
                certified = max(2, int(completed * cert_rate))
                placed = max(1, int(certified * min(0.95, true_openings / (certified + 5.0))))

                pipeline_rows.append({
                    "month": m_str,
                    "district_id": district_id,
                    "trade_id": trade_id,
                    "centre_id": f"TC_{district_id:03d}_{trade_id:02d}",
                    "capacity": cap,
                    "allocated_seats": seats,
                    "enrolled": enrolled,
                    "completed": completed,
                    "certified": certified,
                    "placed": placed,  # Placed recorded for calibration ONLY, not in supply equation
                    "data_mode": "synthetic",
                })

    # Save to Parquet
    evidence_df = pd.DataFrame(evidence_rows)
    pipeline_df = pd.DataFrame(pipeline_rows)

    evidence_parquet = os.path.join(output_dir, "evidence_units.parquet")
    pipeline_parquet = os.path.join(output_dir, "training_pipeline.parquet")

    evidence_df.to_parquet(evidence_parquet, index=False)
    pipeline_df.to_parquet(pipeline_parquet, index=False)

    print(f"[OK] Saved {len(evidence_df)} evidence unit records to {evidence_parquet}")
    print(f"[OK] Saved {len(pipeline_df)} training pipeline records to {pipeline_parquet}")

    return {
        "districts_count": n_districts,
        "trades_count": n_trades,
        "months_count": MONTHS_HISTORY,
        "total_cells": n_districts * n_trades,
        "evidence_rows": len(evidence_df),
        "pipeline_rows": len(pipeline_df),
        "planted_episodes_count": len(planted_episodes),
    }


if __name__ == "__main__":
    ref_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "reference"))
    synth_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "synthetic"))
    dist_csv = os.path.join(ref_dir, "lgd_districts.csv")
    trade_csv = os.path.join(ref_dir, "trades_master.csv")
    stats = generate_synthetic_dataset(synth_dir, dist_csv, trade_csv)
    print(json.dumps(stats, indent=2))
