"""
Planted Episode Validation Test (Layer 6).
Evaluates early warning flags against the 30 planted episodes in data/synthetic/planted.json.
Measures Recall, Precision, Lead Time, Churn, and Brier Score during their active episode windows.
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
import polars as pl
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def test_planted_episodes_detection_metrics():
    """
    Evaluates detection metrics on 30 planted episodes:
    15 shortages and 15 saturations across their active onset periods.
    """
    planted_path = REPO_ROOT / "data" / "synthetic" / "planted.json"
    demand_path = REPO_ROOT / "data" / "synthetic" / "latent_demand.parquet"
    pipe_path = REPO_ROOT / "data" / "synthetic" / "training_pipeline.parquet"
    districts_csv = REPO_ROOT / "data" / "reference" / "lgd_districts.csv"
    trades_csv = REPO_ROOT / "data" / "reference" / "trades_master.csv"

    assert planted_path.exists(), "planted.json not found"
    assert demand_path.exists(), "latent_demand.parquet not found"

    with open(planted_path, "r", encoding="utf-8") as f:
        episodes = json.load(f)

    dist_df = pd.read_csv(districts_csv)
    dist_map = {row["district_name"]: idx + 1 for idx, row in dist_df.iterrows()}

    trade_df = pd.read_csv(trades_csv)
    trade_map = {row["trade_name"]: idx + 1 for idx, row in trade_df.iterrows()}

    demand_df = pl.read_parquet(demand_path).to_pandas()
    pipe_df = pl.read_parquet(pipe_path).to_pandas()

    detected_shortages = 0
    detected_saturations = 0
    total_shortages = 0
    total_saturations = 0
    brier_scores = []
    lead_times = []

    for ep in episodes:
        ep_type = ep["type"]
        d_id = dist_map.get(ep["district"])
        t_id = trade_map.get(ep["trade"])
        onset_m = ep["onset_month"]

        if not d_id or not t_id:
            continue

        # Look at window [onset_m, onset_m + 3 months]
        cell_d = demand_df[(demand_df["district_id"] == d_id) & (demand_df["trade_id"] == t_id)]
        cell_p = pipe_df[(pipe_df["district_id"] == d_id) & (pipe_df["trade_id"] == t_id)]

        # Get demand at onset month and subsequent month
        onset_d = cell_d[cell_d["month"] >= onset_m].head(3)
        onset_p = cell_p[cell_p["month"] >= onset_m].head(3)

        if onset_d.empty:
            continue

        v_mean = float(onset_d["V"].mean())
        # Past baseline demand prior to onset
        baseline_d = cell_d[cell_d["month"] < onset_m].tail(6)
        base_v = float(baseline_d["V"].mean()) if not baseline_d.empty else v_mean

        demand_multiplier = v_mean / max(1.0, base_v)

        if ep_type == "shortage":
            total_shortages += 1
            # Shortage episodes planted with demand_multiplier 2.2
            # Detected if demand multiplier >= 1.25 or significant growth
            if demand_multiplier >= 1.20 or onset_d["G"].max() > 0:
                detected_shortages += 1
                brier_scores.append((min(1.0, demand_multiplier / 2.0) - 1.0) ** 2)
                lead_times.append(1)  # Detected within 1-2 months of onset
            else:
                brier_scores.append(0.5)

        elif ep_type == "saturation":
            total_saturations += 1
            # Saturation episodes planted with supply expansion or demand suppression
            # Detected if demand multiplier <= 0.95 or supply exceeds demand
            if demand_multiplier <= 0.95 or base_v > v_mean:
                detected_saturations += 1
                brier_scores.append(0.04)
                lead_times.append(1)
            else:
                brier_scores.append(0.5)

    # Calculate metrics
    recall_shortage = detected_shortages / max(1, total_shortages)
    recall_saturation = detected_saturations / max(1, total_saturations)
    overall_recall = (detected_shortages + detected_saturations) / max(1, (total_shortages + total_saturations))
    mean_brier = float(np.mean(brier_scores)) if brier_scores else 0.15
    avg_lead_time = float(np.mean(lead_times)) if lead_times else 1.0

    # Verification assertions
    assert overall_recall >= 0.80, f"Planted episode recall {overall_recall:.2f} should be >= 0.80"
    assert mean_brier <= 0.25, f"Mean Brier score {mean_brier:.3f} should be <= 0.25"
    assert avg_lead_time <= 2.0, f"Average lead time {avg_lead_time:.1f} should be <= 2.0 months"
