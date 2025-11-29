import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import date, timedelta
import pandas as pd
import numpy as np
from sqlalchemy import select

from app.ml.feature_engineering import FeatureEngineer
from app.db.models.calculated_indicator import CalculatedIndicator
from app.db.models.ml_feature import MLFeature

@pytest.mark.asyncio
async def test_feature_pipeline_mocked():
    # 1. Setup Mock DB
    mock_db = AsyncMock()
    
    # Setup data for extract_features
    stock_code = "005930"
    start_date = date(2023, 1, 1)
    indicators = []
    for i in range(30):
        calc_date = start_date + timedelta(days=i)
        ind = CalculatedIndicator(
            stock_code=stock_code,
            calculation_date=calc_date,
            per=10.0 + i if i != 5 else None, # Missing value at index 5
            pbr=1.0 + i * 0.1,
            roe=15.0,
            debt_to_equity=50.0,
            current_ratio=200.0,
            operating_margin=20.0,
            profit_growth_yoy=5.0
        )
        indicators.append(ind)
        
    # Mock execute result
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = indicators
    mock_db.execute.return_value = mock_result
    
    # 2. Initialize Engineer
    engineer = FeatureEngineer(mock_db)
    
    # 3. Test Extract
    df = await engineer.extract_features(
        stock_codes=[stock_code],
        start_date=start_date,
        end_date=date(2023, 1, 30)
    )
    
    assert not df.empty
    assert len(df) == 30
    assert "per" in df.columns
    assert df.iloc[5]["per"] is None or np.isnan(df.iloc[5]["per"])
    
    # 4. Test Preprocess
    df_clean = engineer.preprocess_features(df)
    assert not df_clean["per"].isna().any()
    # Check forward fill: index 5 should take value from index 4 (14.0)
    assert df_clean.iloc[5]["per"] == 14.0
    
    # 5. Test Derived Features
    df_derived = engineer.create_derived_features(df_clean)
    assert "per_lag1" in df_derived.columns
    assert "per_roll5_mean" in df_derived.columns
    # Rows with NaNs from lags should be dropped
    # Lag 5 means first 5 rows will have NaNs
    # Roll 20 means first 19 rows will have NaNs
    # So we expect 30 - 19 = 11 rows (actually rolling window includes current row, so index 19 is 20th row)
    # Wait, rolling(20) produces NaN for indices 0..18 (19 NaNs). Index 19 has value.
    # So we lose 19 rows.
    assert len(df_derived) == 30 - 19 
    
    # 6. Test Normalize
    df_norm = engineer.normalize_features(df_derived)
    assert "per" in df_norm.columns
    
    # 7. Test Save
    await engineer.save_features(df_norm)
    
    # Verify save called
    # We expect db.execute to be called for insertion
    # Since we have 5 rows and chunk size is 1000, it should be called once
    assert mock_db.execute.call_count >= 2 # Once for select, once for insert
    
    # Verify commit called
    mock_db.commit.assert_called_once()
