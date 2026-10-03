"""
Global LightGBM Demand Forecaster (Layer 6).
Predicts future labour demand across all district x trade panel series.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
import polars as pl

try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False
    from sklearn.ensemble import HistGradientBoostingRegressor


class GlobalLightGBMForecaster:
    """
    Global Gradient Boosting Forecaster for district x trade panel series.
    Features:
      - Lagged log-openings (lags 1, 2, 3, 6, 12)
      - Rolling stats (3m, 6m, 12m rolling mean and std)
      - Growth rates (G_3m, G_12m)
      - Seasonality (month-of-year, sin/cos cyclical encoding)
      - Employer breadth (B), recency (R), corroboration (I), persistence
      - Categoricals: district_id, trade_id
      - Training supply features: past enrollments and capacity
    """

    def __init__(self, horizons: List[int] = [3, 6, 12], random_state: int = 42):
        self.horizons = horizons
        self.random_state = random_state
        self.models: Dict[int, Union["lgb.LGBMRegressor", "HistGradientBoostingRegressor"]] = {}
        self.residual_stds: Dict[int, float] = {}
        self.feature_names: List[str] = []

    def prepare_features(
        self,
        demand_df: pd.DataFrame,
        pipeline_df: Optional[pd.DataFrame] = None,
    ) -> pd.DataFrame:
        """
        Build panel feature dataset from historical latent demand and training pipeline.
        demand_df columns expected:
          ['month', 'district_id', 'trade_id', 'V', 'B', 'R', 'I', 'P_persist']
        """
        df = demand_df.copy()
        df["month_date"] = pd.to_datetime(df["month"] + "-01")
        df = df.sort_values(["district_id", "trade_id", "month_date"]).reset_index(drop=True)
        
        # Target feature: log(V + 1)
        df["log_v"] = np.log1p(np.maximum(0.0, df["V"].values))

        # Merge pipeline features if provided
        if pipeline_df is not None and not pipeline_df.empty:
            pipe_agg = pipeline_df.groupby(["month", "district_id", "trade_id"])[
                ["capacity", "enrolled", "certified"]
            ].sum().reset_index()
            pipe_agg["log_capacity"] = np.log1p(pipe_agg["capacity"])
            pipe_agg["log_enrolled"] = np.log1p(pipe_agg["enrolled"])
            df = df.merge(pipe_agg[["month", "district_id", "trade_id", "log_capacity", "log_enrolled"]],
                          on=["month", "district_id", "trade_id"], how="left")
            df["log_capacity"] = df["log_capacity"].fillna(0.0)
            df["log_enrolled"] = df["log_enrolled"].fillna(0.0)
        else:
            df["log_capacity"] = 0.0
            df["log_enrolled"] = 0.0

        # Groupby district and trade to construct lag & rolling features
        grouped = df.groupby(["district_id", "trade_id"])
        
        # Lags
        for lag in [1, 2, 3, 6, 12]:
            df[f"lag_{lag}"] = grouped["log_v"].shift(lag)

        # Rolling statistics (using closed='left' equivalent by shifting 1)
        shifted = grouped["log_v"].shift(1)
        df["roll_mean_3"] = grouped["log_v"].transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
        df["roll_mean_6"] = grouped["log_v"].transform(lambda x: x.shift(1).rolling(6, min_periods=1).mean())
        df["roll_mean_12"] = grouped["log_v"].transform(lambda x: x.shift(1).rolling(12, min_periods=1).mean())
        df["roll_std_6"] = grouped["log_v"].transform(lambda x: x.shift(1).rolling(6, min_periods=2).std()).fillna(0.1)

        # Growth rates
        df["growth_3"] = df["log_v"].shift(1) - grouped["log_v"].shift(4)
        df["growth_12"] = df["log_v"].shift(1) - grouped["log_v"].shift(13)

        # Seasonality
        month_num = df["month_date"].dt.month
        df["month_num"] = month_num
        df["sin_month"] = np.sin(2 * np.pi * month_num / 12.0)
        df["cos_month"] = np.cos(2 * np.pi * month_num / 12.0)

        # Ensure breadth, recency, corroboration columns exist
        for col in ["B", "R", "I", "P_persist"]:
            if col not in df.columns:
                df[col] = 1.0

        # Fill remaining missing lag values with backward fill or 0
        lag_cols = [c for c in df.columns if c.startswith("lag_") or c.startswith("roll_") or c.startswith("growth_")]
        df[lag_cols] = df[lag_cols].fillna(0.0)

        return df

    def get_feature_columns(self) -> List[str]:
        return [
            "district_id",
            "trade_id",
            "month_num",
            "sin_month",
            "cos_month",
            "lag_1",
            "lag_2",
            "lag_3",
            "lag_6",
            "lag_12",
            "roll_mean_3",
            "roll_mean_6",
            "roll_mean_12",
            "roll_std_6",
            "growth_3",
            "growth_12",
            "B",
            "R",
            "I",
            "P_persist",
            "log_capacity",
            "log_enrolled",
        ]

    def fit(self, df_features: pd.DataFrame) -> "GlobalLightGBMForecaster":
        """
        Fits a model for each forecast horizon h.
        Target for horizon h: log_v at t+h.
        """
        self.feature_names = self.get_feature_columns()
        grouped = df_features.groupby(["district_id", "trade_id"])

        for h in self.horizons:
            # Construct target for horizon h: shift(-h)
            target_col = f"target_h{h}"
            df_h = df_features.copy()
            df_h[target_col] = grouped["log_v"].shift(-h)
            
            # Filter rows with valid target and complete lag 12 history
            valid_mask = df_h[target_col].notna() & (df_h["month_date"] >= "2022-01-01")
            train_df = df_h[valid_mask]

            X = train_df[self.feature_names].values
            y = train_df[target_col].values

            if HAS_LIGHTGBM:
                model = lgb.LGBMRegressor(
                    n_estimators=120,
                    learning_rate=0.06,
                    num_leaves=31,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    random_state=self.random_state,
                    n_jobs=-1,
                    verbose=-1,
                )
            else:
                model = HistGradientBoostingRegressor(
                    max_iter=120,
                    learning_rate=0.06,
                    random_state=self.random_state,
                )

            model.fit(X, y)
            preds = model.predict(X)
            residuals = y - preds
            self.residual_stds[h] = float(np.std(residuals)) if len(residuals) > 0 else 0.25
            self.models[h] = model

        return self

    def predict(
        self,
        latest_features: pd.DataFrame,
        horizon: int,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Predict for all cells in latest_features for a given horizon h.
        Returns: (y_pred_openings, sigma_h, q10, q90)
        """
        if horizon not in self.models:
            # Pick closest available horizon
            avail_h = min(self.models.keys(), key=lambda k: abs(k - horizon))
            model = self.models[avail_h]
            sigma = self.residual_stds.get(avail_h, 0.25) * np.sqrt(horizon / max(1, avail_h))
        else:
            model = self.models[horizon]
            sigma = self.residual_stds.get(horizon, 0.25)

        X = latest_features[self.feature_names].values
        log_preds = model.predict(X)
        
        # Convert log predictions back to natural openings: exp(log_pred) - 1
        openings_pred = np.maximum(0.0, np.expm1(log_preds))
        
        # Uncalibrated baseline quantiles (conformal calibration updates these)
        q10 = np.maximum(0.0, np.expm1(log_preds - 1.2816 * sigma))
        q90 = np.maximum(0.0, np.expm1(log_preds + 1.2816 * sigma))
        
        return openings_pred, np.full(len(openings_pred), sigma), q10, q90
