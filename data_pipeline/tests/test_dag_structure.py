"""
DAG structure validation tests.

Verifies that both DAGs (daily_price_ingestion, indicator_calculation) are
syntactically valid, have the expected tasks and dependency chains, and
carry correct default arguments — all without requiring a running Airflow
instance.
"""

from datetime import timedelta

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_schedule(dag):
    """Return the schedule string, compatible with Airflow 2.x and 3.x.

    Airflow 3.x removed the ``schedule_interval`` property in favour of
    ``timetable``.  This helper falls back gracefully.
    """
    try:
        return dag.schedule_interval
    except AttributeError:
        return dag.timetable.summary


# ---------------------------------------------------------------------------
# DAG import helpers — loaded once per session
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def daily_dag():
    """Import and return the daily_price_ingestion DAG object."""
    from daily_price_ingestion_dag import dag

    return dag


@pytest.fixture(scope="session")
def indicator_dag():
    """Import and return the indicator_calculation DAG object."""
    from indicator_calculation_dag import dag

    return dag


# ===========================================================================
# daily_price_ingestion DAG
# ===========================================================================


class TestDailyPriceIngestionDagStructure:
    """Structural tests for the daily_price_ingestion DAG."""

    def test_dag_id(self, daily_dag):
        assert daily_dag.dag_id == "daily_price_ingestion"

    def test_schedule(self, daily_dag):
        assert _get_schedule(daily_dag) == "0 18 * * 1-5"

    def test_catchup_disabled(self, daily_dag):
        assert daily_dag.catchup is False

    def test_max_active_runs(self, daily_dag):
        assert daily_dag.max_active_runs == 1

    def test_tags(self, daily_dag):
        assert set(daily_dag.tags) == {"daily", "krx", "prices", "critical"}

    # -- default_args -------------------------------------------------------

    def test_default_args_owner(self, daily_dag):
        assert daily_dag.default_args["owner"] == "data-team"

    def test_default_args_retries(self, daily_dag):
        assert daily_dag.default_args["retries"] == 3

    def test_default_args_retry_delay(self, daily_dag):
        assert daily_dag.default_args["retry_delay"] == timedelta(minutes=5)

    def test_default_args_email(self, daily_dag):
        emails = daily_dag.default_args["email"]
        assert "data-alerts@screener.kr" in emails

    def test_default_args_email_on_failure(self, daily_dag):
        assert daily_dag.default_args["email_on_failure"] is True

    # -- tasks ---------------------------------------------------------------

    EXPECTED_TASK_IDS = {
        "fetch_krx_prices",
        "validate_price_data",
        "load_prices_to_db",
        "check_data_completeness",
        "refresh_timescale_aggregates",
        "log_ingestion_status",
        "trigger_indicator_calculation",
    }

    def test_task_count(self, daily_dag):
        assert len(daily_dag.tasks) == len(self.EXPECTED_TASK_IDS)

    def test_task_ids(self, daily_dag):
        actual_ids = {t.task_id for t in daily_dag.tasks}
        assert actual_ids == self.EXPECTED_TASK_IDS

    # -- dependency chain ----------------------------------------------------

    def test_fetch_to_validate_dependency(self, daily_dag):
        validate = daily_dag.get_task("validate_price_data")
        assert "fetch_krx_prices" in validate.upstream_task_ids

    def test_validate_to_load_dependency(self, daily_dag):
        load = daily_dag.get_task("load_prices_to_db")
        assert "validate_price_data" in load.upstream_task_ids

    def test_load_to_check_dependency(self, daily_dag):
        check = daily_dag.get_task("check_data_completeness")
        assert "load_prices_to_db" in check.upstream_task_ids

    def test_check_to_refresh_dependency(self, daily_dag):
        refresh = daily_dag.get_task("refresh_timescale_aggregates")
        assert "check_data_completeness" in refresh.upstream_task_ids

    def test_refresh_to_trigger_dependency(self, daily_dag):
        trigger = daily_dag.get_task("trigger_indicator_calculation")
        assert "refresh_timescale_aggregates" in trigger.upstream_task_ids

    def test_log_status_depends_on_check_and_trigger(self, daily_dag):
        log_task = daily_dag.get_task("log_ingestion_status")
        assert "check_data_completeness" in log_task.upstream_task_ids
        assert "trigger_indicator_calculation" in log_task.upstream_task_ids

    def test_log_status_trigger_rule(self, daily_dag):
        log_task = daily_dag.get_task("log_ingestion_status")
        assert log_task.trigger_rule == "all_done"

    # -- callable verification -----------------------------------------------

    def test_fetch_task_callable_is_not_deprecated_wrapper(self, daily_dag):
        """The fetch task should use fetch_stock_prices directly, not the
        deprecated fetch_krx_prices wrapper."""
        from daily_price_ingestion_dag import fetch_stock_prices

        fetch_task = daily_dag.get_task("fetch_krx_prices")
        assert fetch_task.python_callable is fetch_stock_prices


# ===========================================================================
# indicator_calculation DAG
# ===========================================================================


class TestIndicatorCalculationDagStructure:
    """Structural tests for the indicator_calculation DAG."""

    def test_dag_id(self, indicator_dag):
        assert indicator_dag.dag_id == "indicator_calculation"

    def test_schedule_is_none(self, indicator_dag):
        schedule = _get_schedule(indicator_dag)
        # Airflow 2.x returns None; Airflow 3.x returns str "None" or "Never"
        assert schedule is None or schedule in ("None", "Never")

    def test_catchup_disabled(self, indicator_dag):
        assert indicator_dag.catchup is False

    def test_max_active_runs(self, indicator_dag):
        assert indicator_dag.max_active_runs == 1

    def test_tags(self, indicator_dag):
        assert set(indicator_dag.tags) == {"indicators", "calculations", "critical"}

    # -- default_args -------------------------------------------------------

    def test_default_args_owner(self, indicator_dag):
        assert indicator_dag.default_args["owner"] == "data-team"

    def test_default_args_retries(self, indicator_dag):
        assert indicator_dag.default_args["retries"] == 2

    def test_default_args_email(self, indicator_dag):
        emails = indicator_dag.default_args["email"]
        assert "data-alerts@screener.kr" in emails

    # -- tasks ---------------------------------------------------------------

    EXPECTED_TASK_IDS = {
        "calculate_indicators",
        "refresh_materialized_views",
        "log_calculation_status",
    }

    def test_task_count(self, indicator_dag):
        assert len(indicator_dag.tasks) == len(self.EXPECTED_TASK_IDS)

    def test_task_ids(self, indicator_dag):
        actual_ids = {t.task_id for t in indicator_dag.tasks}
        assert actual_ids == self.EXPECTED_TASK_IDS

    # -- dependency chain ----------------------------------------------------

    def test_calculate_to_refresh_dependency(self, indicator_dag):
        refresh = indicator_dag.get_task("refresh_materialized_views")
        assert "calculate_indicators" in refresh.upstream_task_ids

    def test_refresh_to_log_dependency(self, indicator_dag):
        log_task = indicator_dag.get_task("log_calculation_status")
        assert "refresh_materialized_views" in log_task.upstream_task_ids

    def test_calculate_has_execution_timeout(self, indicator_dag):
        calc = indicator_dag.get_task("calculate_indicators")
        assert calc.execution_timeout == timedelta(minutes=30)
