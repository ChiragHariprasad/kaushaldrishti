"""
Gap and Early Warning Pipeline Runner (Layer 6).
Computes probabilistic gap distributions, evaluates hysteresis alert state machines,
persists records to the database and parquet artifacts.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
import polars as pl
from sqlalchemy import delete, select

from app.db.models import Alert, AlertHistory, DemandForecast, District, Gap, SupplyForecast, Trade
from app.db.session import async_session_factory
from pipelines.gap.engine import GapEngine
from pipelines.gap.flags import CellSignalInput, HysteresisAlertManager

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
logger = logging.getLogger("kaushaldrishti.gap_runner")


class GapPipelineRunner:
    """
    Orchestrates gap analysis and early warning alert generation.
    """

    def __init__(
        self,
        demand_parquet: Optional[str] = None,
        supply_parquet: Optional[str] = None,
        output_gap_parquet: Optional[str] = None,
        output_alert_parquet: Optional[str] = None,
    ):
        self.demand_parquet = Path(demand_parquet) if demand_parquet else REPO_ROOT / "data" / "synthetic" / "demand_forecasts.parquet"
        self.supply_parquet = Path(supply_parquet) if supply_parquet else REPO_ROOT / "data" / "synthetic" / "supply_forecasts.parquet"
        self.output_gap_parquet = Path(output_gap_parquet) if output_gap_parquet else REPO_ROOT / "data" / "synthetic" / "gaps.parquet"
        self.output_alert_parquet = Path(output_alert_parquet) if output_alert_parquet else REPO_ROOT / "data" / "synthetic" / "alerts.parquet"
        self.gap_engine = GapEngine()
        self.alert_manager = HysteresisAlertManager()

    def run(self) -> Tuple[pd.DataFrame, pd.DataFrame, List[Dict[str, Any]]]:
        """
        Runs the full gap and alert computation across all cells and windows.
        """
        logger.info(f"Loading demand forecasts from {self.demand_parquet}...")
        df_d = pl.read_parquet(self.demand_parquet).to_pandas()

        logger.info(f"Loading supply forecasts from {self.supply_parquet}...")
        df_s = pl.read_parquet(self.supply_parquet).to_pandas()

        origin_month = str(df_d["origin_month"].iloc[0])
        logger.info(f"Computing gaps for origin month {origin_month}...")

        gap_rows: List[Dict[str, Any]] = []
        alert_rows: List[Dict[str, Any]] = []
        history_rows: List[Dict[str, Any]] = []

        # Process each window: 12 (annual target-setting) and 3 (quarterly watch)
        for w in [12, 3]:
            # For w=12, match horizon='12'; for w=3, match horizon='3'
            h_str = str(w)
            sub_d = df_d[df_d["horizon"] == h_str].set_index(["district_id", "trade_id"])
            sub_s = df_s[df_s["window_months"] == w].set_index(["district_id", "trade_id"])

            common_keys = sub_d.index.intersection(sub_s.index)
            logger.info(f"Processing window {w}m: {len(common_keys)} matching cells...")

            for d_id, t_id in common_keys:
                d_row = sub_d.loc[(d_id, t_id)]
                s_row = sub_s.loc[(d_id, t_id)]

                d_mean = float(d_row["mean"])
                d_q10 = float(d_row["q10"])
                d_q90 = float(d_row["q90"])
                d_sigma = max(1e-4, (d_q90 - d_q10) / (2.0 * 1.2816))

                s_mean = float(s_row["s_mean"])
                s_q10 = float(s_row["s_q10"])
                s_q90 = float(s_row["s_q90"])
                s_sigma = max(1e-4, (s_q90 - s_q10) / (2.0 * 1.2816))

                data_mode = str(d_row.get("data_mode", "synthetic"))

                gap_res = self.gap_engine.compute_cell_gap(
                    d_mean=d_mean,
                    d_sigma=d_sigma,
                    s_mean=s_mean,
                    s_sigma=s_sigma,
                    window_months=w,
                )

                # Determine cell confidence based on uncertainty ratio
                spread_ratio = (d_q90 - d_q10) / max(1.0, d_mean)
                if spread_ratio < 0.35:
                    confidence = "High"
                elif spread_ratio < 0.75:
                    confidence = "Medium"
                else:
                    confidence = "Low"

                gap_record = {
                    "origin_month": origin_month,
                    "horizon": h_str,
                    "district_id": int(d_id),
                    "trade_id": int(t_id),
                    "window_months": int(w),
                    "d_mean": gap_res["d_mean"],
                    "s_mean": gap_res["s_mean"],
                    "g_mean": gap_res["g_mean"],
                    "gap_rate": gap_res["gap_rate"],
                    "p_shortage": gap_res["p_shortage"],
                    "p_oversupply": gap_res["p_oversupply"],
                    "tolerance": gap_res["tolerance"],
                    "severity": gap_res["severity"],
                    "status": gap_res["status"],
                    "confidence": confidence,
                    "data_mode": data_mode,
                }
                gap_rows.append(gap_record)

                # Alerts are generated primarily on the standard 12-month window
                if w == 12:
                    # Simulated growth metrics
                    demand_trend = float(gap_res["gap_rate"] * 0.5)
                    capacity_trend = float(0.10 if s_mean > d_mean else -0.05)
                    corroboration_i = 2.0 if confidence == "High" else 1.0

                    sig = CellSignalInput(
                        p_shortage=gap_res["p_shortage"],
                        p_oversupply=gap_res["p_oversupply"],
                        gap_rate=gap_res["gap_rate"],
                        expected_gap=gap_res["g_mean"],
                        demand_trend=demand_trend,
                        capacity_trend=capacity_trend,
                        confidence=confidence,
                        interval_spread=spread_ratio,
                        corroboration_i=corroboration_i,
                    )

                    # State machine evaluation (with simulated prior state persistence)
                    prior_flag = "Stable"
                    prior_count = 1
                    # Planted / high shortage check
                    if gap_res["p_shortage"] >= 0.80 and gap_res["gap_rate"] >= 0.20:
                        prior_flag = "Acute Shortage"
                        prior_count = 2
                    elif 0.60 <= gap_res["p_shortage"] < 0.80:
                        prior_flag = "Emerging Shortage"
                        prior_count = 2
                    elif gap_res["p_oversupply"] >= 0.80 and gap_res["gap_rate"] <= -0.20:
                        prior_flag = "Saturated"
                        prior_count = 2
                    elif 0.60 <= gap_res["p_oversupply"] < 0.80:
                        prior_flag = "Approaching Saturation"
                        prior_count = 2

                    final_flag, persist_count, overlays, reason = self.alert_manager.step(
                        current_flag=prior_flag,
                        persistence_count=prior_count,
                        sig=sig,
                    )

                    # Action text
                    if "Shortage" in final_flag:
                        action = "Review next-cycle seat allocation and expand centre training capacity"
                    elif "Saturat" in final_flag:
                        action = "Consolidate existing training capacity to prevent graduate oversaturation"
                    else:
                        action = "Monitor enrollment and placement trends in next refresh"

                    alert_record = {
                        "origin_month": origin_month,
                        "district_id": int(d_id),
                        "trade_id": int(t_id),
                        "flag": final_flag,
                        "overlays": overlays,
                        "since_month": origin_month,
                        "persistence_count": persist_count,
                        "p_value": gap_res["p_shortage"] if "Shortage" in final_flag else gap_res["p_oversupply"],
                        "expected_gap": gap_res["g_mean"],
                        "demand_trend": round(demand_trend, 3),
                        "capacity_trend": round(capacity_trend, 3),
                        "confidence": confidence,
                        "drivers_json": {
                            "spread_ratio": round(spread_ratio, 2),
                            "gap_rate": gap_res["gap_rate"],
                            "tolerance": gap_res["tolerance"],
                            "status": gap_res["status"],
                        },
                        "suggested_action": action,
                        "data_mode": data_mode,
                    }
                    alert_rows.append(alert_record)

                    if reason:
                        history_rows.append({
                            "district_id": int(d_id),
                            "trade_id": int(t_id),
                            "month": origin_month,
                            "previous_flag": prior_flag,
                            "new_flag": final_flag,
                            "reason": reason,
                        })

        df_gap_out = pd.DataFrame(gap_rows)
        df_alert_out = pd.DataFrame(alert_rows)

        # Save Parquet artifacts
        self.output_gap_parquet.parent.mkdir(parents=True, exist_ok=True)
        pl.from_pandas(df_gap_out).write_parquet(self.output_gap_parquet)
        logger.info(f"Saved {len(df_gap_out)} gap records to {self.output_gap_parquet}")

        self.output_alert_parquet.parent.mkdir(parents=True, exist_ok=True)
        pl.from_pandas(df_alert_out).write_parquet(self.output_alert_parquet)
        logger.info(f"Saved {len(df_alert_out)} alert records to {self.output_alert_parquet}")

        return df_gap_out, df_alert_out, history_rows

    async def persist_to_db(
        self,
        df_gap: pd.DataFrame,
        df_alert: pd.DataFrame,
        history_rows: List[Dict[str, Any]],
    ) -> Dict[str, int]:
        """
        Bulk persist gaps, alerts, and alert histories into the canonical database.
        """
        logger.info("Bulk persisting gaps and alerts to database...")

        gap_objs = [
            Gap(
                origin_month=row["origin_month"],
                horizon=str(row["horizon"]),
                district_id=int(row["district_id"]),
                trade_id=int(row["trade_id"]),
                window_months=int(row["window_months"]),
                d_mean=float(row["d_mean"]),
                s_mean=float(row["s_mean"]),
                g_mean=float(row["g_mean"]),
                gap_rate=float(row["gap_rate"]),
                p_shortage=float(row["p_shortage"]),
                p_oversupply=float(row["p_oversupply"]),
                tolerance=float(row["tolerance"]),
                severity=float(row["severity"]),
                status=str(row["status"]),
                confidence=str(row["confidence"]),
                data_mode=str(row["data_mode"]),
            )
            for _, row in df_gap.iterrows()
        ]

        alert_objs = [
            Alert(
                origin_month=row["origin_month"],
                district_id=int(row["district_id"]),
                trade_id=int(row["trade_id"]),
                flag=str(row["flag"]),
                overlays=row["overlays"],
                since_month=str(row["since_month"]),
                persistence_count=int(row["persistence_count"]),
                p_value=float(row["p_value"]),
                expected_gap=float(row["expected_gap"]),
                demand_trend=float(row["demand_trend"]),
                capacity_trend=float(row["capacity_trend"]),
                confidence=str(row["confidence"]),
                drivers_json=row["drivers_json"],
                suggested_action=str(row["suggested_action"]),
                data_mode=str(row["data_mode"]),
            )
            for _, row in df_alert.iterrows()
        ]

        hist_objs = [
            AlertHistory(
                district_id=int(r["district_id"]),
                trade_id=int(r["trade_id"]),
                month=str(r["month"]),
                previous_flag=str(r["previous_flag"]),
                new_flag=str(r["new_flag"]),
                reason=str(r["reason"]),
            )
            for r in history_rows
        ]

        async with async_session_factory() as session:
            async with session.begin():
                origin_m = str(df_gap["origin_month"].iloc[0])
                await session.execute(delete(Gap).where(Gap.origin_month == origin_m))
                await session.execute(delete(Alert).where(Alert.origin_month == origin_m))

                batch_size = 5000
                for i in range(0, len(gap_objs), batch_size):
                    session.add_all(gap_objs[i : i + batch_size])
                for i in range(0, len(alert_objs), batch_size):
                    session.add_all(alert_objs[i : i + batch_size])
                if hist_objs:
                    session.add_all(hist_objs)

            await session.commit()

        counts = {
            "gaps": len(gap_objs),
            "alerts": len(alert_objs),
            "alert_history": len(hist_objs),
        }
        logger.info(f"[OK] Persisted {counts['gaps']} gaps and {counts['alerts']} alerts.")
        return counts
