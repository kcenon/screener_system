import pytest
import pandas as pd
import numpy as np
import os
from app.ml.prediction_model import StockPredictionModel


@pytest.fixture
def sample_data():
    # Create dummy data for 100 days
    dates = pd.date_range(start="2023-01-01", periods=100)
    data = {
        "calculation_date": dates,
        "stock_code": ["005930"] * 100,
        "close": np.linspace(100, 200, 100) + np.random.normal(
            0, 5, 100
        ),  # Upward trend
        "feature1": np.random.rand(100),
        "feature2": np.random.rand(100),
    }
    df = pd.DataFrame(data)
    return df


def test_prepare_data(sample_data):
    model = StockPredictionModel()
    X, y = model.prepare_data(
        sample_data, target_col="close", horizon=5, threshold=0.01
    )

    assert not X.empty
    assert not y.empty
    assert len(X) == len(y)
    # Horizon is 5, so last 5 rows should be dropped
    assert len(X) == 100 - 5
    assert "feature1" in X.columns
    assert "feature2" in X.columns
    assert "close" not in X.columns  # Target col should be dropped from features
    assert "stock_code" not in X.columns


def test_train_predict_lightgbm(sample_data):
    model = StockPredictionModel(model_type="lightgbm")
    X, y = model.prepare_data(sample_data, target_col="close", horizon=5)

    # Split train/test
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train = y.iloc[:split_idx]

    model.train(X_train, y_train)
    preds = model.predict(X_test)

    assert len(preds) == len(X_test)
    assert set(np.unique(preds)).issubset({0, 1, 2})


def test_train_predict_xgboost(sample_data):
    model = StockPredictionModel(model_type="xgboost")
    X, y = model.prepare_data(sample_data, target_col="close", horizon=5)

    # Split train/test
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train = y.iloc[:split_idx]

    model.train(X_train, y_train)
    preds = model.predict(X_test)

    assert len(preds) == len(X_test)
    assert set(np.unique(preds)).issubset({0, 1, 2})


def test_evaluate(sample_data):
    model = StockPredictionModel(model_type="lightgbm")
    X, y = model.prepare_data(sample_data, target_col="close", horizon=5)

    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    model.train(X_train, y_train)
    metrics = model.evaluate(X_test, y_test)

    assert "accuracy" in metrics
    assert "f1_score" in metrics
    assert "report" in metrics
    assert 0 <= metrics["accuracy"] <= 1


def test_optimize_hyperparameters(sample_data):
    model = StockPredictionModel(model_type="lightgbm")
    X, y = model.prepare_data(sample_data, target_col="close", horizon=5)

    # Run small optimization
    best_params = model.optimize_hyperparameters(X, y, n_trials=2)

    assert isinstance(best_params, dict)
    assert "num_leaves" in best_params
    assert model.params == best_params


def test_save_load_model(sample_data, tmp_path):
    model = StockPredictionModel(model_type="lightgbm")
    X, y = model.prepare_data(sample_data, target_col="close", horizon=5)
    model.train(X, y)

    save_path = tmp_path / "model.joblib"
    model.save_model(str(save_path))

    assert os.path.exists(save_path)

    new_model = StockPredictionModel(model_type="lightgbm")
    new_model.load_model(str(save_path))

    assert new_model.model is not None
