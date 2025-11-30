import joblib
import lightgbm as lgb
import numpy as np
import optuna
import pandas as pd
import xgboost as xgb
from typing import Any, Dict, Optional, Tuple

from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import TimeSeriesSplit


class StockPredictionModel:
    """
    Stock price movement prediction model using LightGBM or XGBoost.
    """

    def __init__(
        self, model_type: str = "lightgbm", params: Optional[Dict[str, Any]] = None
    ):
        self.model_type = model_type
        self.params = params or {}
        self.model = None

    def prepare_data(
        self,
        df: pd.DataFrame,
        target_col: str = "close",
        horizon: int = 5,
        threshold: float = 0.02,
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Generate labels and split features/target.

        Labels:
        0: Down (Return < -threshold)
        1: Flat (-threshold <= Return <= threshold)
        2: Up (Return > threshold)
        """
        if df.empty:
            return pd.DataFrame(), pd.Series()

        df = df.copy()

        # Calculate future return
        # Note: We need 'close' price to calculate return.
        # If 'close' is not in df, we assume it's passed or available.
        # For now, let's assume 'close' is available or we use 'price_change_1d'
        # accumulated?
        # Actually, feature engineering should have provided necessary columns.
        # If we only have features, we can't calculate future return unless we have
        # future prices.
        # So this method assumes df contains raw price data or we pass it separately.
        # Let's assume df has 'close' column for now.

        if target_col not in df.columns:
            # If close price is not available, we can't generate labels.
            # But maybe we are in inference mode?
            # For training, we need labels.
            raise ValueError(f"Target column '{target_col}' not found in DataFrame")

        # Future return = (Price[t+horizon] - Price[t]) / Price[t]
        future_return = df[target_col].shift(-horizon) / df[target_col] - 1

        # Generate labels
        conditions = [
            (future_return < -threshold),
            (future_return > threshold)
        ]
        choices = [0, 2]  # 0: Down, 2: Up
        labels = np.select(conditions, choices, default=1)  # 1: Flat

        # Remove last 'horizon' rows where target is NaN
        valid_indices = ~np.isnan(future_return)
        # Drop columns that are not features (like date, stock_code, target_col)
        # We assume all other numeric columns are features
        drop_cols = ["stock_code", "calculation_date", target_col]
        feature_cols = [
            c
            for c in df.columns
            if c not in drop_cols and pd.api.types.is_numeric_dtype(df[c])
        ]

        X = df.loc[valid_indices, feature_cols]
        y = pd.Series(labels[valid_indices], index=X.index)

        return X, y

    def train(self, features: pd.DataFrame, labels: pd.Series):
        """
        Train the model.
        """
        if self.model_type == "lightgbm":
            train_data = lgb.Dataset(features, label=labels)
            default_params = {
                "objective": "multiclass",
                "num_class": 3,
                "metric": "multi_logloss",
                "verbosity": -1,
                "boosting_type": "gbdt",
            }
            params = {**default_params, **self.params}
            self.model = lgb.train(params, train_data)

        elif self.model_type == "xgboost":
            default_params = {
                "objective": "multi:softprob",
                "num_class": 3,
                "eval_metric": "mlogloss",
            }
            params = {**default_params, **self.params}
            self.model = xgb.XGBClassifier(**params)
            self.model.fit(features, labels)

        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")

    def predict(self, features: pd.DataFrame) -> np.ndarray:
        """
        Predict labels.
        """
        if self.model is None:
            raise ValueError("Model not trained")

        if self.model_type == "lightgbm":
            # LightGBM returns probabilities for multiclass
            probs = self.model.predict(features)
            return np.argmax(probs, axis=1)
        elif self.model_type == "xgboost":
            return self.model.predict(features)
        return np.array([])

    def evaluate(
        self, test_features: pd.DataFrame, test_labels: pd.Series
    ) -> Dict[str, Any]:
        """
        Evaluate model performance.
        """
        predictions = self.predict(test_features)

        accuracy = accuracy_score(test_labels, predictions)
        f1 = f1_score(test_labels, predictions, average="weighted")
        report = classification_report(test_labels, predictions, output_dict=True)

        return {"accuracy": accuracy, "f1_score": f1, "report": report}

    def optimize_hyperparameters(
        self, features: pd.DataFrame, labels: pd.Series, n_trials: int = 20
    ) -> Dict[str, Any]:
        """
        Optimize hyperparameters using Optuna with TimeSeriesSplit.
        """

        def objective(trial):
            if self.model_type == "lightgbm":
                param = {
                    "objective": "multiclass",
                    "num_class": 3,
                    "metric": "multi_logloss",
                    "verbosity": -1,
                    "boosting_type": "gbdt",
                    "lambda_l1": trial.suggest_float("lambda_l1", 1e-8, 10.0, log=True),
                    "lambda_l2": trial.suggest_float("lambda_l2", 1e-8, 10.0, log=True),
                    "num_leaves": trial.suggest_int("num_leaves", 2, 256),
                    "feature_fraction": trial.suggest_float(
                        "feature_fraction", 0.4, 1.0
                    ),
                    "bagging_fraction": trial.suggest_float(
                        "bagging_fraction", 0.4, 1.0
                    ),
                    "bagging_freq": trial.suggest_int("bagging_freq", 1, 7),
                    "min_child_samples": trial.suggest_int("min_child_samples", 5, 100),
                }
            else:  # xgboost
                param = {
                    "objective": "multi:softprob",
                    "num_class": 3,
                    "eval_metric": "mlogloss",
                    "booster": "gbtree",
                    "lambda": trial.suggest_float("lambda", 1e-8, 1.0, log=True),
                    "alpha": trial.suggest_float("alpha", 1e-8, 1.0, log=True),
                    "max_depth": trial.suggest_int("max_depth", 1, 9),
                    "eta": trial.suggest_float("eta", 1e-8, 1.0, log=True),
                    "gamma": trial.suggest_float("gamma", 1e-8, 1.0, log=True),
                    "grow_policy": trial.suggest_categorical(
                        "grow_policy", ["depthwise", "lossguide"]
                    ),
                }

            # Time Series Cross Validation
            tscv = TimeSeriesSplit(n_splits=3)
            scores = []

            for train_index, val_index in tscv.split(features):
                X_train, X_val = features.iloc[train_index], features.iloc[val_index]
                y_train, y_val = labels.iloc[train_index], labels.iloc[val_index]

                model = StockPredictionModel(self.model_type, param)
                model.train(X_train, y_train)
                metrics = model.evaluate(X_val, y_val)
                scores.append(metrics["f1_score"])

            return np.mean(scores)

        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=n_trials)

        self.params = study.best_params
        return study.best_params

    def save_model(self, path: str):
        """Save model to file"""
        joblib.dump(self.model, path)

    def load_model(self, path: str):
        """Load model from file"""
        self.model = joblib.load(path)
