"""
Demand Forecast Pipeline Runner (Layer 6).
Generates ensemble forecasts across all 144 districts x 40 trades for
horizons 3, 6, 12 months and cohort-aligned duration L.
Persists records to Parquet and canonical database.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
import polars as pl
from sqlalchemy import select, delete

from app.db.models import DemandForecast, District, Trade
from app.db.session import async_session_factory
from pipelines.forecast.ensemble import EnsembleDemandForecaster
from pipelines.forecast.lightgbm_model import GlobalLightGBMForecaster
from pipelines.forecast.state_space import StateSpaceForecaster

logger = logging.getLogger("kaushaldrishti.forecast_runner")


REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class ForecastPipelineRunner:
    """
    Executes the full forecasting pipeline and populates DemandForecast table.
    """

    def __init__(
        self,
        demand_parquet: Optional[str] = None,
        trades_csv: Optional[str] = None,
        output_parquet: Optional[str] = None,
    ):
        self.demand_parquet = Path(demand_parquet) if demand_parquet else REPO_ROOT / "data" / "synthetic" / "latent_demand.parquet"
        self.trades_csv = Path(trades_csv) if trades_csv else REPO_ROOT / "data" / "reference" / "trades_master.csv"
        self.output_parquet = Path(output_parquet) if output_parquet else REPO_ROOT / "data" / "synthetic" / "demand_forecasts.parquet"

    def run(self) -> pd.DataFrame:
        """
        Generates forecasts for latest available month.
        """
        logger.info(f"Loading latent demand from {self.demand_parquet}...")
        df_pl = pl.read_parquet(self.demand_parquet)
        df = df_pl.to_pandas()

        logger.info(f"Loading trades master from {self.trades_csv}...")
        trades_df = pd.read_csv(self.trades_csv)
        # Map trade_name/index to course_months
        trade_cohort_map = {}
        for idx, row in trades_df.iterrows():
            # Trade ID in DB is 1-indexed matching CSV row order
            trade_id = idx + 1
            course_m = int(row.get("course_months", 6))
            trade_cohort_map[trade_id] = course_m

        latest_month = df["month"].max()
        logger.info(f"Origin month for forecasting: {latest_month}")

        # Train global LightGBM on historical series
        lgbm = GlobalLightGBMForecaster(horizons=[3, 6, 12])
        features_df = lgbm.prepare_features(df)
        lgbm.fit(features_df)

        latest_data = df[df["month"] == latest_month].copy()
        latest_features = features_df[features_df["month"] == latest_month].copy()

        # Build forecasts
        forecast_rows: List[Dict[str, Any]] = []
        ss = StateSpaceForecaster()
        ens = EnsembleDemandForecaster(horizons=[3, 6, 12])

        # Precompute LightGBM predictions for 3, 6, 12
        lgbm_preds: Dict[int, np.ndarray] = {}
        lgbm_sigmas: Dict[int, np.ndarray] = {}
        for h in [3, 6, 12]:
            m_pred, s_pred, _, _ = lgbm.predict(latest_features, h)
            lgbm_preds[h] = m_pred
            lgbm_sigmas[h] = s_pred

        logger.info(f"Forecasting for {len(latest_data)} district x trade cells...")

        for idx, (_, row) in enumerate(latest_data.iterrows()):
            d_id = int(row["district_id"])
            t_id = int(row["trade_id"])
            m_t = float(row["m"])
            b_t = float(row["slope"])
            p_t = float(row["P"])
            data_mode = str(row.get("data_mode", "synthetic"))
            cohort_L = trade_cohort_map.get(t_id, 6)

            # Retrieve cell history (past 24 months) for ETS & Naive
            cell_hist = df[(df["district_id"] == d_id) & (df["trade_id"] == t_id)]["V"].tolist()

            # Horizons to process: 3, 6, 12, and cohort
            horizons_to_run = [3, 6, 12]
            
            for h in horizons_to_run:
                l_pred = float(lgbm_preds[h][idx]) if idx < len(lgbm_preds[h]) else None
                l_sig = float(lgbm_sigmas[h][idx]) if idx < len(lgbm_sigmas[h]) else None

                res = ens.predict_cell(
                    history_openings=cell_hist,
                    m_t=m_t,
                    b_t=b_t,
                    p_t=p_t,
                    horizon=h,
                    lgbm_pred_openings=l_pred,
                    lgbm_sigma=l_sig,
                )

                forecast_rows.append({
                    "origin_month": latest_month,
                    "horizon": str(h),
                    "district_id": d_id,
                    "trade_id": t_id,
                    "mean": round(res["mean"], 2),
                    "q10": round(res["q10"], 2),
                    "q90": round(res["q90"], 2),
                    "model": "ensemble",
                    "fallback_level": 0,
                    "data_mode": data_mode,
                })

            # Cohort-aligned horizon
            # If cohort_L is not in [3, 6, 12], generate dedicated prediction
            # Otherwise, duplicate with horizon='cohort'
            if cohort_L in [3, 6, 12]:
                matching = [r for r in forecast_rows[-3:] if r["horizon"] == str(cohort_L)][0]
                cohort_res = {
                    "mean": matching["mean"],
                    "q10": matching["q10"],
                    "q90": matching["q90"],
                }
            else:
                res_c = ens.predict_cell(
                    history_openings=cell_hist,
                    m_t=m_t,
                    b_t=b_t,
                    p_t=p_t,
                    horizon=cohort_L,
                )
                cohort_res = {
                    "mean": round(res_c["mean"], 2),
                    "q10": round(res_c["q10"], 2),
                    "q90": round(res_c["q90"], 2),
                }

            forecast_rows.append({
                "origin_month": latest_month,
                "horizon": "cohort",
                "district_id": d_id,
                "trade_id": t_id,
                "mean": cohort_res["mean"],
                "q10": cohort_res["q10"],
                "q90": cohort_res["q90"],
                "model": "ensemble",
                "fallback_level": 0,
                "data_mode": data_mode,
            })

        forecast_df = pd.DataFrame(forecast_rows)
        logger.info(f"Generated {len(forecast_df)} forecast records.")

        # Save to Parquet
        Path(self.output_parquet).parent.mkdir(parents=True, exist_ok=True)
        pl.from_pandas(forecast_df).write_parquet(self.output_parquet)
        logger.info(f"Saved Parquet artifact to {self.output_parquet}")

        return forecast_df

    async def persist_to_db(self, forecast_df: pd.DataFrame) -> int:
        """
        Bulk persist forecast rows to the database.
        """
        logger.info(f"Bulk persisting {len(forecast_df)} forecast records into database...")
        records = [
            DemandForecast(
                origin_month=row["origin_month"],
                horizon=row["horizon"],
                district_id=int(row["district_id"]),
                trade_id=int(row["trade_id"]),
                mean=float(row["mean"]),
                q10=float(row["q10"]),
                q90=float(row["q90"]),
                model=str(row["model"]),
                fallback_level=int(row["fallback_level"]),
                data_mode=str(row["data_mode"]),
            )
            for _, row in forecast_df.iterrows()
        ]

        async with async_session_factory() as session:
            async with session.begin():
                # Clear previous forecasts for this origin_month to allow idempotency
                latest_m = str(forecast_df["origin_month"].iloc[0])
                await session.execute(
                    delete(DemandForecast).where(DemandForecast.origin_month == latest_m)
                )
                # Bulk insert in batches of 5000
                batch_size = 5000
                for i in range(0, len(records), batch_size):
                    session.add_all(records[i : i + batch_size])
            await session.commit()

        logger.info(f"[OK] Successfully persisted {len(records)} forecasts into database.")
        return len(records)
