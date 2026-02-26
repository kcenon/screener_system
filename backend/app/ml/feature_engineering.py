from datetime import date
from typing import List

import numpy as np
import pandas as pd
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.calculated_indicator import CalculatedIndicator
from app.db.models.ml_feature import MLFeature


class FeatureEngineer:
    """
    Pipeline for transforming raw indicators into ML-ready features.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def extract_features(
        self, stock_codes: List[str], start_date: date, end_date: date
    ) -> pd.DataFrame:
        """
        Fetch raw indicators from database.
        """
        query = (
            select(CalculatedIndicator)
            .where(CalculatedIndicator.stock_code.in_(stock_codes))
            .where(CalculatedIndicator.calculation_date >= start_date)
            .where(CalculatedIndicator.calculation_date <= end_date)
            .order_by(
                CalculatedIndicator.stock_code, CalculatedIndicator.calculation_date
            )
        )

        result = await self.db.execute(query)
        indicators = result.scalars().all()

        if not indicators:
            return pd.DataFrame()

        # Convert to DataFrame
        data = [
            {
                "stock_code": ind.stock_code,
                "calculation_date": ind.calculation_date,
                "per": float(ind.per) if ind.per is not None else None,
                "pbr": float(ind.pbr) if ind.pbr is not None else None,
                "roe": float(ind.roe) if ind.roe is not None else None,
                "debt_to_equity": (
                    float(ind.debt_to_equity)
                    if ind.debt_to_equity is not None
                    else None
                ),
                "current_ratio": (
                    float(ind.current_ratio) if ind.current_ratio is not None else None
                ),
                "operating_margin": (
                    float(ind.operating_margin)
                    if ind.operating_margin is not None
                    else None
                ),
                "profit_growth_yoy": (
                    float(ind.profit_growth_yoy)
                    if ind.profit_growth_yoy is not None
                    else None
                ),
            }
            for ind in indicators
        ]

        df = pd.DataFrame(data)
        df["calculation_date"] = pd.to_datetime(df["calculation_date"])
        return df

    def preprocess_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values.
        """
        if df.empty:
            return df

        # Sort for time-series operations
        df = df.sort_values(["stock_code", "calculation_date"])

        # Forward fill within each stock group
        # Note: groupby().ffill() might drop the grouper column
        df_filled = df.groupby("stock_code").ffill()
        df_filled["stock_code"] = df["stock_code"]
        df = df_filled

        # Fill remaining NaNs with 0 (or median, depending on strategy)
        # For now, using 0 for simplicity, but interpolation might be better
        df = df.fillna(0)

        return df

    def create_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create lag features and rolling statistics.
        """
        if df.empty:
            return df

        features = ["close", "per", "pbr", "roe"]

        for feature in features:
            if feature not in df.columns:
                continue

            # Lag features (1 day, 5 days)
            df[f"{feature}_lag1"] = df.groupby("stock_code")[feature].shift(1)
            df[f"{feature}_lag5"] = df.groupby("stock_code")[feature].shift(5)

            # Rolling mean (5 days, 20 days)
            df[f"{feature}_roll5_mean"] = (
                df.groupby("stock_code")[feature]
                .rolling(window=5)
                .mean()
                .reset_index(0, drop=True)
            )
            df[f"{feature}_roll20_mean"] = (
                df.groupby("stock_code")[feature]
                .rolling(window=20)
                .mean()
                .reset_index(0, drop=True)
            )

        # Drop rows with NaNs created by shifting/rolling
        df = df.dropna()
        return df

    def normalize_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize features (Z-score normalization).
        """
        if df.empty:
            return df

        numeric_cols = df.select_dtypes(include=[np.number]).columns

        # Group by date to normalize across stocks for that day (cross-sectional)
        # Or group by stock to normalize over time?
        # Usually for stock prediction, we might want cross-sectional normalization
        # (rank or z-score per day)
        # Let's do Z-score per day for now

        def zscore(x):
            if x.std() == 0:
                return x - x.mean()
            return (x - x.mean()) / x.std()

        # Apply z-score per date group for numeric columns
        # Note: This might be slow for large datasets
        # Alternatively, we can just do global normalization or per-stock normalization
        # Let's stick to simple per-column normalization for now to keep it simple

        for col in numeric_cols:
            if col in ["stock_code", "calculation_date"]:
                continue
            mean = df[col].mean()
            std = df[col].std()
            if std != 0:
                df[col] = (df[col] - mean) / std

        return df

    async def save_features(self, df: pd.DataFrame):
        """
        Save processed features to ml_features table.
        """
        if df.empty:
            return

        # Prepare data for insertion
        values = []
        for _, row in df.iterrows():
            feature_data = row.drop(["stock_code", "calculation_date"]).to_dict()
            # Convert numpy types to python types for JSON serialization
            feature_data = {k: float(v) for k, v in feature_data.items()}

            values.append(
                {
                    "stock_code": row["stock_code"],
                    "calculation_date": row["calculation_date"].date(),
                    "feature_data": feature_data,
                }
            )

        # Batch insert/upsert
        # Using chunks to avoid query too large
        chunk_size = 1000
        for i in range(0, len(values), chunk_size):
            chunk = values[i : i + chunk_size]
            stmt = insert(MLFeature).values(chunk)
            stmt = stmt.on_conflict_do_update(
                index_elements=["stock_code", "calculation_date"],
                set_={"feature_data": stmt.excluded.feature_data},
            )
            await self.db.execute(stmt)
        await self.db.commit()
