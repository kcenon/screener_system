"""
Tests for XCom data passing between Airflow tasks.

Covers:
- End-to-end flow: convert_chart_data_to_price_data → XCom push → validate_price_data
- XCom key naming conventions
- Multi-task data propagation

Requires: apache-airflow (installed in CI, skipped locally)
"""

import pytest
from unittest.mock import MagicMock

airflow = pytest.importorskip("airflow", reason="Airflow required (CI only)")

from daily_price_ingestion_dag import (  # noqa: E402
    convert_chart_data_to_price_data,
    validate_price_data,
)
from kis_api_client import ChartData  # noqa: E402


def _make_chart_data(stock_code, date, close_price=70000.0, volume=10000000):
    """Helper to create ChartData with sensible defaults."""
    return ChartData(
        stock_code=stock_code,
        date=date,
        open_price=close_price * 0.98,
        high_price=close_price * 1.02,
        low_price=close_price * 0.97,
        close_price=close_price,
        volume=volume,
        trading_value=close_price * volume,
    )


# ============================================================================
# End-to-end XCom flow
# ============================================================================


class TestXComEndToEnd:
    """Tests for data flowing through XCom between DAG tasks."""

    def test_convert_then_validate(self, mock_xcom_store, mock_task_instance):
        """Chart data converted and pushed via XCom validates successfully."""
        # Step 1: Convert chart data to price format
        charts = [
            _make_chart_data("005930", "20240603", 70000, 10000000),
            _make_chart_data("000660", "20240603", 125000, 5000000),
            _make_chart_data("035420", "20240603", 200000, 3000000),
        ]
        prices = convert_chart_data_to_price_data(charts, "005930")

        # Step 2: Simulate upstream task pushing to XCom
        # (In the real DAG, fetch_krx_prices pushes prices_data)
        mock_xcom_store["fetch_krx_prices::prices_data"] = prices

        ctx = {
            "task_instance": mock_task_instance,
            "ti": mock_task_instance,
            "ds": "2024-06-03",
        }

        # Step 3: Validate should accept all records
        result = validate_price_data(**ctx)
        assert result == 3
        assert "valid_prices" in mock_xcom_store
        assert len(mock_xcom_store["valid_prices"]) == 3

    def test_mixed_valid_invalid_flow(self, mock_xcom_store, mock_task_instance):
        """Mixed valid/invalid records flow correctly through XCom."""
        # Step 1: Convert valid charts
        valid_charts = [
            _make_chart_data(f"00{i:04d}", "20240603", 70000 + i * 1000, 10000000)
            for i in range(98)
        ]
        valid_prices = convert_chart_data_to_price_data(valid_charts, "dummy")

        # Step 2: Add invalid records (missing fields)
        invalid_records = [
            {"stock_code": "BAD01", "trade_date": "20240603"},
            {"stock_code": "BAD02", "trade_date": "20240603"},
        ]

        all_data = valid_prices + invalid_records
        mock_xcom_store["fetch_krx_prices::prices_data"] = all_data

        ctx = {
            "task_instance": mock_task_instance,
            "ti": mock_task_instance,
            "ds": "2024-06-03",
        }

        # Step 3: Validate filters out bad records
        result = validate_price_data(**ctx)
        assert result == 98
        valid_codes = {r["stock_code"] for r in mock_xcom_store["valid_prices"]}
        assert "BAD01" not in valid_codes
        assert "BAD02" not in valid_codes

    def test_xcom_pull_key_convention(self, mock_xcom_store, mock_task_instance):
        """validate_price_data uses the correct XCom pull key."""
        # The validate task pulls with task_ids="fetch_krx_prices", key="prices_data"
        # XCom mock resolves this as "fetch_krx_prices::prices_data"
        prices = [
            {
                "stock_code": "005930",
                "trade_date": "20240603",
                "open_price": 70000.0,
                "high_price": 72000.0,
                "low_price": 69000.0,
                "close_price": 71000.0,
                "volume": 10000000,
                "trading_value": 710000000000.0,
                "market_cap": None,
            }
        ]
        mock_xcom_store["fetch_krx_prices::prices_data"] = prices

        ctx = {
            "task_instance": mock_task_instance,
            "ti": mock_task_instance,
            "ds": "2024-06-03",
        }

        result = validate_price_data(**ctx)
        assert result == 1

        # Verify xcom_pull was called
        mock_task_instance.xcom_pull.assert_called()

    def test_validated_data_is_pushed_for_downstream(
        self, mock_xcom_store, mock_task_instance
    ):
        """After validation, data is pushed with 'valid_prices' key for downstream."""
        prices = [
            {
                "stock_code": "005930",
                "trade_date": "20240603",
                "open_price": 70000.0,
                "high_price": 72000.0,
                "low_price": 69000.0,
                "close_price": 71000.0,
                "volume": 10000000,
                "trading_value": 710000000000.0,
                "market_cap": 430000000000000,
            }
        ]
        mock_xcom_store["fetch_krx_prices::prices_data"] = prices

        ctx = {
            "task_instance": mock_task_instance,
            "ti": mock_task_instance,
            "ds": "2024-06-03",
        }

        validate_price_data(**ctx)

        # Check that xcom_push was called with correct key
        mock_task_instance.xcom_push.assert_called()
        push_args = mock_task_instance.xcom_push.call_args
        assert push_args[1]["key"] == "valid_prices" or push_args[0][0] == "valid_prices"


# ============================================================================
# convert_chart_data_to_price_data output format
# ============================================================================


class TestConvertOutputFormat:
    """Tests that converted data matches the expected XCom transport format."""

    def test_output_is_list_of_dicts(self):
        """Converted data is a list of plain dicts (JSON-serializable for XCom)."""
        charts = [_make_chart_data("005930", "20240603")]
        result = convert_chart_data_to_price_data(charts, "005930")

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], dict)

    def test_output_has_required_keys(self):
        """Each dict has the keys validate_price_data expects."""
        charts = [_make_chart_data("005930", "20240603")]
        result = convert_chart_data_to_price_data(charts, "005930")
        record = result[0]

        required_keys = {
            "stock_code",
            "trade_date",
            "open_price",
            "high_price",
            "low_price",
            "close_price",
            "volume",
        }
        assert required_keys.issubset(record.keys())

    def test_stock_code_from_argument(self):
        """stock_code in output comes from function argument, not ChartData."""
        chart = _make_chart_data("005930", "20240603")
        result = convert_chart_data_to_price_data([chart], "000660")
        assert result[0]["stock_code"] == "000660"

    def test_date_format_preserved(self):
        """Date is preserved as YYYYMMDD string."""
        chart = _make_chart_data("005930", "20240603")
        result = convert_chart_data_to_price_data([chart], "005930")
        assert result[0]["trade_date"] == "20240603"
