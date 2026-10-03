"""
Supply Pipeline Orchestrator (Layer 5).
Simulates supply pipelines, computes window supply S_W(t+L),
and writes supply forecasts to Parquet and the database.
"""

import asyncio
import os
import sys
from collections import defaultdict
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from app.db.models import SupplyForecast
from app.db.session import async_session_factory
from pipelines.supply.engine import PipelineCohortInput, SupplyDynamicsEngine


SYNTHETIC_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "synthetic")
)


def run_supply_pipeline(n_draws: int = 2000) -> Dict[str, Any]:
    """
    Computes supply forecasts across all cells for latest origin month.
    """
    pipeline_parquet = os.path.join(SYNTHETIC_DIR, "training_pipeline.parquet")
    if not os.path.exists(pipeline_parquet):
        raise FileNotFoundError(f"Training pipeline file not found at {pipeline_parquet}. Run generator first.")

    print(f"[INFO] Loading training pipeline data from {pipeline_parquet}...")
    pipe_df = pd.read_parquet(pipeline_parquet)

    ref_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "reference"))
    trades_df = pd.read_csv(os.path.join(ref_dir, "trades_master.csv"))
    course_l_map = {idx + 1: int(row["course_months"]) for idx, row in trades_df.iterrows()}

    engine = SupplyDynamicsEngine(n_draws=n_draws)

    latest_month = pipe_df["month"].max()
    latest_df = pipe_df[pipe_df["month"] == latest_month]

    supply_rows = []

    print(f"[INFO] Computing supply forecasts for month {latest_month} across {len(latest_df)} centres/trades...")

    for _, row in latest_df.iterrows():
        d_id = int(row["district_id"])
        t_id = int(row["trade_id"])
        course_l = course_l_map.get(t_id, 6)

        # Notice: placed column is NOT passed to PipelineCohortInput
        cohort = PipelineCohortInput(
            capacity=int(row["capacity"]),
            allocated_seats=int(row["allocated_seats"]),
            enrolled=int(row["enrolled"]),
            completed=int(row["completed"]),
            certified=int(row["certified"]),
            course_months=course_l,
        )

        # 1. 12-Month Target Setting Window Supply
        w12_res = engine.compute_window_supply([cohort], window_months=12)
        supply_rows.append({
            "origin_month": latest_month,
            "target_month": f"{latest_month}_W12",
            "district_id": d_id,
            "trade_id": t_id,
            "window_months": 12,
            "s_mean": w12_res["s_mean"],
            "s_q10": w12_res["s_q10"],
            "s_q90": w12_res["s_q90"],
            "basis": w12_res["basis"],
            "data_mode": "synthetic",
        })

        # 2. 3-Month Quarterly Watch Window Supply
        w3_res = engine.compute_window_supply([cohort], window_months=3)
        supply_rows.append({
            "origin_month": latest_month,
            "target_month": f"{latest_month}_W3",
            "district_id": d_id,
            "trade_id": t_id,
            "window_months": 3,
            "s_mean": w3_res["s_mean"],
            "s_q10": w3_res["s_q10"],
            "s_q90": w3_res["s_q90"],
            "basis": w3_res["basis"],
            "data_mode": "synthetic",
        })

    supply_df = pd.DataFrame(supply_rows)
    output_parquet = os.path.join(SYNTHETIC_DIR, "supply_forecasts.parquet")
    supply_df.to_parquet(output_parquet, index=False)
    print(f"[OK] Saved {len(supply_df)} supply forecasts to {output_parquet}")

    return {
        "status": "success",
        "origin_month": latest_month,
        "forecast_rows": len(supply_df),
        "output_file": output_parquet,
    }


async def load_supply_forecasts_to_db():
    """
    Bulk loads supply forecasts into database.
    """
    parquet_path = os.path.join(SYNTHETIC_DIR, "supply_forecasts.parquet")
    if not os.path.exists(parquet_path):
        return

    print("[INFO] Bulk loading supply forecasts into database...")
    df = pd.read_parquet(parquet_path)
    latest_month = df["origin_month"].max()

    async with async_session_factory() as session:
        from sqlalchemy import delete
        await session.execute(delete(SupplyForecast).where(SupplyForecast.origin_month == latest_month))

        objs = [
            SupplyForecast(
                origin_month=row["origin_month"],
                target_month=row["target_month"],
                district_id=int(row["district_id"]),
                trade_id=int(row["trade_id"]),
                window_months=int(row["window_months"]),
                s_mean=float(row["s_mean"]),
                s_q10=float(row["s_q10"]),
                s_q90=float(row["s_q90"]),
                basis=str(row["basis"]),
                data_mode=str(row["data_mode"]),
            )
            for _, row in df.iterrows()
        ]
        session.add_all(objs)
        await session.commit()
        print(f"[OK] Loaded {len(objs)} supply forecasts into database.")


if __name__ == "__main__":
    res = run_supply_pipeline(n_draws=2000)
    print(res)
    asyncio.run(load_supply_forecasts_to_db())
