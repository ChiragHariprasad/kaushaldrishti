"""
Demand Pipeline Orchestrator (Layer 4).
Runs Kalman fusion, empirical Bayes partial pooling, frozen baseline calibration,
LDI calculation, and exact source attributions across all cells.
"""

import asyncio
import os
import sys
from collections import defaultdict
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from app.db.models import District, LatentDemand, SourceContribution, Trade
from app.db.session import async_session_factory
from pipelines.demand.index import DemandIndexEngine
from pipelines.demand.kalman import KalmanFusion


SYNTHETIC_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "synthetic")
)


def run_demand_pipeline(months_limit: int = 48, force_regenerate: bool = False) -> Dict[str, Any]:
    """
    Executes Kalman fusion and LDI calculation across all cells.
    """
    latent_parquet = os.path.join(SYNTHETIC_DIR, "latent_demand.parquet")
    contrib_parquet = os.path.join(SYNTHETIC_DIR, "source_contributions.parquet")

    if not force_regenerate and os.path.exists(latent_parquet) and os.path.exists(contrib_parquet):
        print(f"[INFO] Existing latent demand parquet found at {latent_parquet}. Skipping recomputation.")
        df_lat = pd.read_parquet(latent_parquet)
        df_con = pd.read_parquet(contrib_parquet)
        return {
            "status": "cached",
            "latent_rows": len(df_lat),
            "contribution_rows": len(df_con),
        }

    evidence_parquet = os.path.join(SYNTHETIC_DIR, "evidence_units.parquet")
    if not os.path.exists(evidence_parquet):
        raise FileNotFoundError(f"Evidence units not found at {evidence_parquet}. Run generator first.")

    print(f"[INFO] Loading evidence units from {evidence_parquet}...")
    evidence_df = pd.read_parquet(evidence_parquet)

    # Reference data paths
    ref_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "reference"))
    dist_df = pd.read_csv(os.path.join(ref_dir, "lgd_districts.csv"))
    trade_df = pd.read_csv(os.path.join(ref_dir, "trades_master.csv"))

    pop_map = {idx + 1: row["population_working_age"] for idx, row in dist_df.iterrows()}
    trade_name_map = {idx + 1: row["trade_name"] for idx, row in trade_df.iterrows()}

    # Group evidence fast by (month, district_id, trade_id)
    cell_groups = defaultdict(list)
    for m, d, t, src, z, v, gp, gr in zip(
        evidence_df["month"],
        evidence_df["district_id"],
        evidence_df["trade_id"],
        evidence_df["source_id"],
        evidence_df["z"],
        evidence_df["v"],
        evidence_df["gate_pass"],
        evidence_df["gate_reason"],
    ):
        cell_groups[(m, int(d), int(t))].append({
            "source_id": src,
            "z": float(z),
            "v": float(v),
            "gate_pass": bool(gp),
            "gate_reason": gr,
        })

    kf = KalmanFusion(phi=0.9, q_theta=0.04, q_b=0.01)
    index_engine = DemandIndexEngine()

    all_months = sorted(list(set(evidence_df["month"])))[:months_limit]
    n_districts = len(dist_df)
    n_trades = len(trade_df)

    cell_states = {}
    for d_id in range(1, n_districts + 1):
        for t_id in range(1, n_trades + 1):
            cell_states[(d_id, t_id)] = {
                "m": 3.0,
                "p": 0.5,
                "b": 0.0,
                "history": [],
            }

    latent_demand_rows = []
    source_contrib_rows = []
    baseline_intensities = defaultdict(list)

    print(f"[INFO] Running Kalman fusion for {len(all_months)} months across {n_districts * n_trades} cells...")

    for m_idx, m_str in enumerate(all_months):
        is_baseline_period = (m_idx < 24)

        trade_district_means = defaultdict(list)
        trade_district_vars = defaultdict(list)

        for d_id in range(1, n_districts + 1):
            pop = pop_map.get(d_id, 500000)

            for t_id in range(1, n_trades + 1):
                t_name = trade_name_map.get(t_id, f"Trade_{t_id}")
                st = cell_states[(d_id, t_id)]

                m_prior, p_prior, b_prior = kf.predict(st["m"], st["p"], st["b"])
                obs = cell_groups.get((m_str, d_id, t_id), [])

                if obs:
                    update_res = kf.update(m_prior, p_prior, obs)
                    m_post = update_res["m_post"]
                    p_post = update_res["p_post"]
                    contributions = update_res["contributions"]
                else:
                    m_post = m_prior
                    p_post = p_prior
                    contributions = []

                st["m"] = m_post
                st["p"] = p_post
                st["b"] = 0.9 * st["b"] + 0.1 * (m_post - m_prior)
                st["history"].append(m_post)

                trade_district_means[t_id].append(m_post)
                trade_district_vars[t_id].append(p_post)

                for c in contributions:
                    source_contrib_rows.append({
                        "month": m_str,
                        "district_id": d_id,
                        "trade_id": t_id,
                        "source_id": c["source_id"],
                        "weight": c["weight"],
                        "contribution": c["contribution"],
                    })

                iota = index_engine.compute_intensity(m_post, pop)
                if is_baseline_period:
                    baseline_intensities[t_name].append(iota)

        tau2_per_trade = {}
        for t_id in range(1, n_trades + 1):
            tau2_per_trade[t_id] = kf.estimate_tau2(
                trade_district_means[t_id], trade_district_vars[t_id]
            )

        for d_id in range(1, n_districts + 1):
            pop = pop_map.get(d_id, 500000)

            for t_id in range(1, n_trades + 1):
                t_name = trade_name_map.get(t_id, f"Trade_{t_id}")
                st = cell_states[(d_id, t_id)]
                m_curr = st["m"]
                p_curr = st["p"]

                state_mean = float(np.mean(trade_district_means[t_id]))
                tau2 = tau2_per_trade[t_id]

                m_pooled, p_pooled, shrink_lambda, data_share = kf.apply_partial_pooling(
                    m_curr, p_curr, state_mean, tau2
                )

                iota, ldi, ldi_lo, ldi_hi = index_engine.compute_ldi(t_name, m_pooled, p_pooled, pop)

                descriptors = index_engine.compute_descriptors(
                    m=m_pooled,
                    m_history=st["history"],
                    source_weights={"ncs": 0.35, "portal": 0.45, "eshram": 0.20},
                    source_ages_days={"ncs": 15.0, "portal": 5.0, "eshram": 20.0},
                    source_growth_signs={"ncs": 1, "portal": 1, "eshram": 1},
                    source_independence_groups={"ncs": "govt_job", "portal": "portal", "eshram": "registry"},
                )

                confidence = index_engine.assign_confidence(
                    p=p_pooled,
                    data_share=data_share,
                    n_independent_sources=3,
                    fallback_level=0,
                )

                latent_demand_rows.append({
                    "month": m_str,
                    "district_id": d_id,
                    "trade_id": t_id,
                    "m": round(m_pooled, 4),
                    "P": round(p_pooled, 4),
                    "slope": round(st["b"], 4),
                    "data_share": round(data_share, 4),
                    "fallback_level": 0,
                    "n_gated_sources": 3,
                    "intensity_iota": iota,
                    "ldi": ldi,
                    "ldi_lo": ldi_lo,
                    "ldi_hi": ldi_hi,
                    "confidence": confidence,
                    "V": descriptors["V"],
                    "G": descriptors["G"],
                    "R": descriptors["R"],
                    "P_persist": descriptors["P_persist"],
                    "B": descriptors["B"],
                    "I": descriptors["I"],
                    "data_mode": "synthetic",
                })

    index_engine.save_frozen_baseline(baseline_intensities)

    latent_df = pd.DataFrame(latent_demand_rows)
    contrib_df = pd.DataFrame(source_contrib_rows)

    latent_df.to_parquet(latent_parquet, index=False)
    contrib_df.to_parquet(contrib_parquet, index=False)

    print(f"[OK] Saved {len(latent_df)} latent demand rows to {latent_parquet}")
    print(f"[OK] Saved {len(contrib_df)} source contribution rows to {contrib_parquet}")

    return {
        "status": "success",
        "latent_rows": len(latent_df),
        "contribution_rows": len(contrib_df),
        "months_processed": len(all_months),
        "total_cells": n_districts * n_trades,
    }


async def load_latent_demand_to_db():
    """
    Bulk loads latest demand estimates into the database for high-speed API querying.
    """
    latent_parquet = os.path.join(SYNTHETIC_DIR, "latent_demand.parquet")
    contrib_parquet = os.path.join(SYNTHETIC_DIR, "source_contributions.parquet")

    if not os.path.exists(latent_parquet):
        return

    print("[INFO] Bulk loading latest latent demand into database...")
    df_latent = pd.read_parquet(latent_parquet)
    latest_month = df_latent["month"].max()
    df_latest = df_latent[df_latent["month"] == latest_month]

    df_contrib = pd.read_parquet(contrib_parquet)
    df_contrib_latest = df_contrib[df_contrib["month"] == latest_month]

    async with async_session_factory() as session:
        from sqlalchemy import delete
        await session.execute(delete(LatentDemand).where(LatentDemand.month == latest_month))
        await session.execute(delete(SourceContribution).where(SourceContribution.month == latest_month))

        latent_objs = [
            LatentDemand(
                month=row["month"],
                district_id=int(row["district_id"]),
                trade_id=int(row["trade_id"]),
                m=float(row["m"]),
                P=float(row["P"]),
                slope=float(row["slope"]),
                data_share=float(row["data_share"]),
                fallback_level=int(row["fallback_level"]),
                n_gated_sources=int(row["n_gated_sources"]),
                intensity_iota=float(row["intensity_iota"]),
                ldi=float(row["ldi"]),
                ldi_lo=float(row["ldi_lo"]),
                ldi_hi=float(row["ldi_hi"]),
                confidence=str(row["confidence"]),
                V=float(row["V"]),
                G=float(row["G"]),
                R=float(row["R"]),
                P_persist=int(row["P_persist"]),
                B=float(row["B"]),
                I=float(row["I"]),
                data_mode=str(row["data_mode"]),
            )
            for _, row in df_latest.iterrows()
        ]
        session.add_all(latent_objs)

        contrib_objs = [
            SourceContribution(
                month=row["month"],
                district_id=int(row["district_id"]),
                trade_id=int(row["trade_id"]),
                source_id=str(row["source_id"]),
                weight=float(row["weight"]),
                contribution=float(row["contribution"]),
            )
            for _, row in df_contrib_latest.head(10000).iterrows()
        ]
        session.add_all(contrib_objs)

        await session.commit()
        print(f"[OK] Bulk loaded {len(latent_objs)} latent demand records and {len(contrib_objs)} contributions into database.")


if __name__ == "__main__":
    res = run_demand_pipeline(months_limit=48)
    print(res)
    asyncio.run(load_latent_demand_to_db())
