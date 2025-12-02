from datetime import datetime, timedelta

import mlflow
import numpy as np
from airflow import DAG
from airflow.operators.python import PythonOperator

# Default arguments for the DAG
default_args = {
    "owner": "ml-team",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    "daily_stock_prediction_retrain",
    default_args=default_args,
    description="Daily retraining of stock prediction model",
    schedule_interval="0 2 * * *",  # 2 AM KST daily
    start_date=datetime(2025, 11, 1),
    catchup=False,
    tags=["ml", "prediction"],
)


def extract_training_data(**context):
    """Extract last 2 years of OHLCV and indicator data"""
    # Placeholder for data extraction logic
    # In reality, this would query the database or feature store
    print("Extracting training data...")
    # Mock data
    data = {"dates": [], "prices": []}
    context["task_instance"].xcom_push(key="data", value=data)
    return f"Extracted data"


def engineer_features(**context):
    """Apply feature engineering pipeline"""
    # Placeholder for feature engineering
    print("Engineering features...")
    # Mock features
    X = np.random.rand(100, 60, 4)
    y = np.random.randint(0, 2, 100)

    context["task_instance"].xcom_push(key="X", value=X.tolist())  # JSON serializable
    context["task_instance"].xcom_push(key="y", value=y.tolist())
    return f"Engineered features"


def train_model(**context):
    """Train model and log to MLflow"""
    print("Training model...")
    X = np.array(
        context["task_instance"].xcom_pull(key="X", task_ids="engineer_features")
    )
    y = np.array(
        context["task_instance"].xcom_pull(key="y", task_ids="engineer_features")
    )

    # Mock training
    metrics = {"accuracy": 0.75}

    # Log to MLflow (mocked for DAG test)
    # mlflow.start_run()
    # mlflow.log_metrics(metrics)
    # mlflow.end_run()

    context["task_instance"].xcom_push(key="metrics", value=metrics)
    return f"Model trained with accuracy: {metrics['accuracy']:.4f}"


def compare_with_production(**context):
    """Compare new model with current production model"""
    print("Comparing models...")
    new_metrics = context["task_instance"].xcom_pull(
        key="metrics", task_ids="train_model"
    )

    # Mock production metrics
    prod_accuracy = 0.70

    improvement = new_metrics["accuracy"] - prod_accuracy
    should_promote = improvement >= 0.02

    context["task_instance"].xcom_push(key="promote", value=should_promote)
    return f"Improvement: {improvement:.4f}, Promote: {should_promote}"


def promote_model(**context):
    """Promote new model to production if better"""
    should_promote = context["task_instance"].xcom_pull(
        key="promote", task_ids="compare_models"
    )

    if should_promote:
        print("Promoting model to Production...")
        # mlflow.transition_model_version_stage(...)
        return "Promoted to Production"
    else:
        print("Not promoting.")
        return "No promotion"


# Define tasks
task_extract = PythonOperator(
    task_id="extract_data",
    python_callable=extract_training_data,
    dag=dag,
)

task_features = PythonOperator(
    task_id="engineer_features",
    python_callable=engineer_features,
    dag=dag,
)

task_train = PythonOperator(
    task_id="train_model",
    python_callable=train_model,
    dag=dag,
)

task_compare = PythonOperator(
    task_id="compare_models",
    python_callable=compare_with_production,
    dag=dag,
)

task_promote = PythonOperator(
    task_id="promote_model",
    python_callable=promote_model,
    dag=dag,
)

# Define dependencies
task_extract >> task_features >> task_train >> task_compare >> task_promote
