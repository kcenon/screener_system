"""
Shared test fixtures for data pipeline tests.

Provides mock Airflow context, XCom simulation, and DAG import helpers
so that DAG structure and task functions can be tested without a running
Airflow instance.
"""

import os
import sys
import types
from datetime import datetime
from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# Path setup — make DAG and script modules importable
# ---------------------------------------------------------------------------

_pipeline_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_dags_path = os.path.join(_pipeline_root, "dags")
_scripts_path = os.path.join(_pipeline_root, "scripts")

for _p in (_dags_path, _scripts_path):
    if _p not in sys.path:
        sys.path.insert(0, _p)


# ---------------------------------------------------------------------------
# Airflow 3.x provider compatibility stubs
# ---------------------------------------------------------------------------
#
# In apache-airflow-providers-postgres 6.x (Airflow 3.x), the
# ``operators/`` sub-package was removed.  PostgresOperator is replaced
# by SQLExecuteQueryOperator from apache-airflow-providers-common-sql.
#
# For DAG structure tests we only need operator classes that register
# tasks in the DAG correctly (inheriting from BaseOperator).  The stubs
# below let us import DAG files unchanged.
# ---------------------------------------------------------------------------


def _ensure_postgres_operator_importable():
    """Create a backward-compat stub for PostgresOperator if missing."""
    try:
        from airflow.providers.postgres.operators.postgres import PostgresOperator  # noqa: F401

        return  # Already available (Airflow 2.x or compat shim)
    except (ImportError, ModuleNotFoundError):
        pass

    from airflow.models.baseoperator import BaseOperator

    class _StubPostgresOperator(BaseOperator):
        """Minimal PostgresOperator stub for DAG structure testing."""

        template_fields = ("sql",)

        def __init__(self, sql="", postgres_conn_id="default", **kwargs):
            super().__init__(**kwargs)
            self.sql = sql
            self.postgres_conn_id = postgres_conn_id

        def execute(self, context):
            raise NotImplementedError("Stub — not for execution")

    # Wire up the module hierarchy so `from … import PostgresOperator` works
    operators_pkg = types.ModuleType("airflow.providers.postgres.operators")
    operators_pkg.__path__ = []
    operators_pkg.__package__ = "airflow.providers.postgres.operators"
    sys.modules["airflow.providers.postgres.operators"] = operators_pkg

    postgres_mod = types.ModuleType("airflow.providers.postgres.operators.postgres")
    postgres_mod.PostgresOperator = _StubPostgresOperator
    postgres_mod.__package__ = "airflow.providers.postgres.operators"
    sys.modules["airflow.providers.postgres.operators.postgres"] = postgres_mod


# Run once at import time — before any DAG module is loaded
_ensure_postgres_operator_importable()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_xcom_store():
    """In-memory XCom key/value store shared across a single test."""
    return {}


@pytest.fixture()
def mock_task_instance(mock_xcom_store):
    """Fake Airflow TaskInstance with working xcom_push / xcom_pull."""
    ti = MagicMock()

    def _push(key, value):
        mock_xcom_store[key] = value

    def _pull(task_ids=None, key="return_value"):
        lookup = f"{task_ids}::{key}" if task_ids else key
        return mock_xcom_store.get(lookup, mock_xcom_store.get(key))

    ti.xcom_push = MagicMock(side_effect=_push)
    ti.xcom_pull = MagicMock(side_effect=_pull)
    return ti


@pytest.fixture()
def airflow_context(mock_task_instance):
    """Minimal Airflow **context dict passed to PythonOperator callables."""
    return {
        "task_instance": mock_task_instance,
        "ti": mock_task_instance,
        "ds": "2024-06-03",
        "logical_date": datetime(2024, 6, 3, 9, 0, 0),
        "execution_date": datetime(2024, 6, 3, 9, 0, 0),
    }
