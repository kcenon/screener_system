"""
Tests for data validation and transformation functions.

Covers:
- convert_chart_data_to_price_data(): KIS ChartData → price dict conversion
- validate_price_data(): price data quality validation with error categorization

Requires: apache-airflow (installed in CI, skipped locally)
"""

import pytest
from unittest.mock import MagicMock, patch
from dataclasses import dataclass
from typing import Optional

airflow = pytest.importorskip("airflow", reason="Airflow required (CI only)")

from daily_price_ingestion_dag import (  # noqa: E402
    convert_chart_data_to_price_data,
    validate_price_data,
)
from kis_api_client import ChartData  # noqa: E402


# ============================================================================
# convert_chart_data_to_price_data
# ============================================================================


class TestConvertChartDataToPriceData:
    """Tests for converting KIS ChartData to pipeline price format."""

    def test_basic_conversion(self):
        """Single ChartData is correctly mapped to price dict."""
        chart = ChartData(
            stock_code="005930",
            date="20240603",
            open_price=72000.0,
            high_price=73000.0,
            low_price=71500.0,
            close_price=72500.0,
            volume=10000000,
            trading_value=725000000000.0,
        )

        result = convert_chart_data_to_price_data([chart], "005930")

        assert len(result) == 1
        r = result[0]
        assert r["stock_code"] == "005930"
        assert r["trade_date"] == "20240603"
        assert r["open_price"] == 72000.0
        assert r["high_price"] == 73000.0
        assert r["low_price"] == 71500.0
        assert r["close_price"] == 72500.0
        assert r["volume"] == 10000000
        assert r["trading_value"] == 725000000000.0
        assert r["market_cap"] is None

    def test_multiple_records(self):
        """Multiple ChartData objects are all converted."""
        charts = [
            ChartData("005930", "20240601", 70000, 71000, 69000, 70500, 5000000),
            ChartData("005930", "20240602", 70500, 72000, 70000, 71500, 6000000),
            ChartData("005930", "20240603", 71500, 73000, 71000, 72500, 7000000),
        ]

        result = convert_chart_data_to_price_data(charts, "005930")

        assert len(result) == 3
        assert [r["trade_date"] for r in result] == [
            "20240601",
            "20240602",
            "20240603",
        ]

    def test_empty_list(self):
        """Empty input returns empty output."""
        result = convert_chart_data_to_price_data([], "005930")
        assert result == []

    def test_trading_value_none_when_missing(self):
        """ChartData without trading_value maps to None."""
        chart = ChartData(
            stock_code="005930",
            date="20240603",
            open_price=72000.0,
            high_price=73000.0,
            low_price=71500.0,
            close_price=72500.0,
            volume=10000000,
        )

        result = convert_chart_data_to_price_data([chart], "005930")
        assert result[0]["trading_value"] is None

    def test_trading_value_preserved_when_present(self):
        """ChartData with trading_value preserves the value."""
        chart = ChartData(
            stock_code="005930",
            date="20240603",
            open_price=72000.0,
            high_price=73000.0,
            low_price=71500.0,
            close_price=72500.0,
            volume=10000000,
            trading_value=500000000.0,
        )

        result = convert_chart_data_to_price_data([chart], "005930")
        assert result[0]["trading_value"] == 500000000.0

    def test_stock_code_from_argument_used(self):
        """Stock code argument overrides ChartData stock_code."""
        chart = ChartData("005930", "20240603", 72000, 73000, 71500, 72500, 10000000)

        result = convert_chart_data_to_price_data([chart], "000660")
        assert result[0]["stock_code"] == "000660"

    def test_market_cap_always_none(self):
        """Market cap is always None for KIS chart data."""
        chart = ChartData("005930", "20240603", 72000, 73000, 71500, 72500, 10000000)

        result = convert_chart_data_to_price_data([chart], "005930")
        assert result[0]["market_cap"] is None


# ============================================================================
# validate_price_data
# ============================================================================


def _make_valid_record(stock_code="005930", **overrides):
    """Helper to create a valid price record with optional overrides."""
    record = {
        "stock_code": stock_code,
        "trade_date": "20240603",
        "open_price": 72000.0,
        "high_price": 73000.0,
        "low_price": 71500.0,
        "close_price": 72500.0,
        "volume": 10000000,
        "trading_value": 725000000000.0,
        "market_cap": 430000000000000,
    }
    record.update(overrides)
    return record


class TestValidatePriceData:
    """Tests for price data validation logic."""

    def _build_context(self, mock_xcom_store, mock_task_instance, prices_data):
        """Seed XCom and return Airflow context for validate_price_data."""
        mock_xcom_store["fetch_krx_prices::prices_data"] = prices_data
        return {
            "task_instance": mock_task_instance,
            "ti": mock_task_instance,
            "ds": "2024-06-03",
        }

    def test_all_valid_records(
        self, mock_xcom_store, mock_task_instance
    ):
        """All valid records pass validation and are pushed to XCom."""
        data = [_make_valid_record(f"00{i:04d}") for i in range(100)]
        ctx = self._build_context(mock_xcom_store, mock_task_instance, data)

        result = validate_price_data(**ctx)

        assert result == 100
        assert "valid_prices" in mock_xcom_store
        assert len(mock_xcom_store["valid_prices"]) == 100

    def test_missing_required_fields(
        self, mock_xcom_store, mock_task_instance
    ):
        """Records missing required fields are filtered out."""
        valid = [_make_valid_record(f"00{i:04d}") for i in range(98)]
        invalid = [
            {"stock_code": "BAD01", "trade_date": "20240603"},  # missing close_price, volume
            {"trade_date": "20240603", "close_price": 100, "volume": 50},  # missing stock_code
        ]
        ctx = self._build_context(mock_xcom_store, mock_task_instance, valid + invalid)

        result = validate_price_data(**ctx)

        assert result == 98
        valid_codes = {r["stock_code"] for r in mock_xcom_store["valid_prices"]}
        assert "BAD01" not in valid_codes

    def test_invalid_price_relationship(
        self, mock_xcom_store, mock_task_instance
    ):
        """Records where high < low are flagged but not fatal if under 5%."""
        valid = [_make_valid_record(f"00{i:04d}") for i in range(99)]
        invalid = [_make_valid_record("BAD01", high_price=100.0, low_price=200.0)]
        ctx = self._build_context(mock_xcom_store, mock_task_instance, valid + invalid)

        result = validate_price_data(**ctx)

        # The invalid record is flagged but the test should still pass
        # since 1/100 < 5%
        assert result == 99

    def test_negative_close_price(
        self, mock_xcom_store, mock_task_instance
    ):
        """Records with negative close_price are invalidated."""
        valid = [_make_valid_record(f"00{i:04d}") for i in range(99)]
        invalid = [_make_valid_record("BAD01", close_price=-100.0)]
        ctx = self._build_context(mock_xcom_store, mock_task_instance, valid + invalid)

        result = validate_price_data(**ctx)
        assert result == 99

    def test_negative_volume(
        self, mock_xcom_store, mock_task_instance
    ):
        """Records with negative volume are invalidated."""
        valid = [_make_valid_record(f"00{i:04d}") for i in range(99)]
        invalid = [_make_valid_record("BAD01", volume=-500)]
        ctx = self._build_context(mock_xcom_store, mock_task_instance, valid + invalid)

        result = validate_price_data(**ctx)
        assert result == 99

    def test_missing_market_cap_is_warning_only(
        self, mock_xcom_store, mock_task_instance
    ):
        """Missing market_cap is a warning, not an error."""
        data = [_make_valid_record("005930", market_cap=None)]
        ctx = self._build_context(mock_xcom_store, mock_task_instance, data)

        result = validate_price_data(**ctx)

        # market_cap=None should NOT cause the record to be invalid
        assert result == 1
        assert len(mock_xcom_store["valid_prices"]) == 1

    def test_over_5_percent_invalid_raises(
        self, mock_xcom_store, mock_task_instance
    ):
        """Raises ValueError when >5% of records are invalid."""
        valid = [_make_valid_record(f"00{i:04d}") for i in range(90)]
        invalid = [
            {"stock_code": f"BAD{i:02d}", "trade_date": "20240603"}
            for i in range(10)
        ]  # 10/100 = 10% > 5%
        ctx = self._build_context(mock_xcom_store, mock_task_instance, valid + invalid)

        with pytest.raises(ValueError, match="Too many invalid records"):
            validate_price_data(**ctx)

    def test_exactly_5_percent_invalid_passes(
        self, mock_xcom_store, mock_task_instance
    ):
        """Exactly 5% invalid records passes (threshold is >5%, not >=5%)."""
        valid = [_make_valid_record(f"00{i:04d}") for i in range(95)]
        invalid = [
            {"stock_code": f"BAD{i:02d}", "trade_date": "20240603"}
            for i in range(5)
        ]  # 5/100 = 5% — exactly at threshold
        ctx = self._build_context(mock_xcom_store, mock_task_instance, valid + invalid)

        result = validate_price_data(**ctx)
        assert result == 95

    def test_no_data_raises(
        self, mock_xcom_store, mock_task_instance
    ):
        """Raises ValueError when no data received from XCom."""
        mock_xcom_store.clear()
        ctx = {
            "task_instance": mock_task_instance,
            "ti": mock_task_instance,
            "ds": "2024-06-03",
        }

        with pytest.raises(ValueError, match="No price data received"):
            validate_price_data(**ctx)

    def test_empty_list_raises(
        self, mock_xcom_store, mock_task_instance
    ):
        """Raises ValueError when empty list received."""
        ctx = self._build_context(mock_xcom_store, mock_task_instance, [])

        with pytest.raises(ValueError, match="No price data received"):
            validate_price_data(**ctx)

    def test_valid_data_pushed_to_xcom(
        self, mock_xcom_store, mock_task_instance
    ):
        """Valid records are pushed as 'valid_prices' key."""
        data = [_make_valid_record("005930"), _make_valid_record("000660")]
        ctx = self._build_context(mock_xcom_store, mock_task_instance, data)

        validate_price_data(**ctx)

        mock_task_instance.xcom_push.assert_called_once()
        call_args = mock_task_instance.xcom_push.call_args
        assert call_args[1]["key"] == "valid_prices" or call_args[0][0] == "valid_prices"

    def test_price_zero_close_is_invalid(
        self, mock_xcom_store, mock_task_instance
    ):
        """Close price of exactly 0 is invalid (must be positive)."""
        valid = [_make_valid_record(f"00{i:04d}") for i in range(99)]
        invalid = [_make_valid_record("BAD01", close_price=0)]
        ctx = self._build_context(mock_xcom_store, mock_task_instance, valid + invalid)

        result = validate_price_data(**ctx)
        assert result == 99

    def test_none_close_price_is_missing_field(
        self, mock_xcom_store, mock_task_instance
    ):
        """None close_price is treated as missing required field."""
        valid = [_make_valid_record(f"00{i:04d}") for i in range(99)]
        invalid = [_make_valid_record("BAD01", close_price=None)]
        ctx = self._build_context(mock_xcom_store, mock_task_instance, valid + invalid)

        result = validate_price_data(**ctx)
        assert result == 99
