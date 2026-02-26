"""
Tests for KRX API Client.

Covers:
- KRXAPIClient initialization and configuration
- authenticate(): mock mode and mocked HTTP responses
- fetch_daily_prices(): mock data, market filtering, date validation, response parsing
- fetch_market_summary(): mock mode and mocked HTTP
- _transform_response(): valid/invalid record handling
- Context manager and utility functions
"""

import pytest
from unittest.mock import patch, MagicMock
import requests

from krx_api_client import (
    KRXAPIClient,
    Market,
    PriceData,
    RateLimiter,
    create_client,
)


# ============================================================================
# Initialization
# ============================================================================


class TestKRXAPIClientInit:
    """Tests for KRXAPIClient initialization."""

    def test_mock_mode_explicit(self):
        """Explicit use_mock=True activates mock mode."""
        client = KRXAPIClient(use_mock=True)
        assert client.use_mock is True

    def test_mock_mode_from_env(self, monkeypatch):
        """KRX_USE_MOCK env var activates mock mode."""
        monkeypatch.setenv("KRX_USE_MOCK", "true")
        client = KRXAPIClient()
        assert client.use_mock is True

    def test_real_mode_default(self, monkeypatch):
        """Default mode is real (non-mock) when env is unset."""
        monkeypatch.delenv("KRX_USE_MOCK", raising=False)
        monkeypatch.delenv("KRX_API_KEY", raising=False)
        client = KRXAPIClient(use_mock=False)
        assert client.use_mock is False

    def test_api_key_from_argument(self):
        """API key passed as argument is used."""
        client = KRXAPIClient(api_key="test-key", use_mock=True)
        assert client.api_key == "test-key"

    def test_api_key_from_env(self, monkeypatch):
        """API key falls back to KRX_API_KEY env var."""
        monkeypatch.setenv("KRX_API_KEY", "env-key")
        client = KRXAPIClient(use_mock=True)
        assert client.api_key == "env-key"

    def test_base_url_default(self):
        """Default base URL is the KRX production endpoint."""
        client = KRXAPIClient(use_mock=True)
        assert client.base_url == KRXAPIClient.DEFAULT_BASE_URL

    def test_base_url_from_env(self, monkeypatch):
        """KRX_API_BASE_URL env var overrides default."""
        monkeypatch.setenv("KRX_API_BASE_URL", "https://custom.api.kr")
        client = KRXAPIClient(use_mock=True)
        assert client.base_url == "https://custom.api.kr"

    def test_custom_timeout_and_retries(self):
        """Custom timeout and max_retries are stored."""
        client = KRXAPIClient(use_mock=True, timeout=60, max_retries=5)
        assert client.timeout == 60
        assert client.max_retries == 5

    def test_session_created(self):
        """Session is created during init."""
        client = KRXAPIClient(use_mock=True)
        assert client.session is not None

    def test_rate_limiter_created(self):
        """RateLimiter is created during init."""
        client = KRXAPIClient(use_mock=True)
        assert isinstance(client.rate_limiter, RateLimiter)


# ============================================================================
# authenticate
# ============================================================================


class TestAuthenticate:
    """Tests for KRXAPIClient.authenticate()."""

    def test_mock_mode_returns_true(self):
        """Mock mode skips authentication and returns True."""
        client = KRXAPIClient(use_mock=True)
        assert client.authenticate() is True

    def test_no_api_key_returns_false(self):
        """Missing API key returns False."""
        client = KRXAPIClient(api_key=None, use_mock=False)
        client.api_key = None
        assert client.authenticate() is False

    def test_successful_auth(self):
        """Successful /auth/verify call returns True."""
        client = KRXAPIClient(api_key="valid-key", use_mock=False)
        with patch.object(client, "_make_request", return_value={"status": "ok"}):
            assert client.authenticate() is True

    def test_401_returns_false(self):
        """HTTP 401 returns False."""
        client = KRXAPIClient(api_key="bad-key", use_mock=False)
        mock_response = MagicMock()
        mock_response.status_code = 401
        http_error = requests.exceptions.HTTPError(response=mock_response)
        with patch.object(client, "_make_request", side_effect=http_error):
            assert client.authenticate() is False

    def test_network_error_returns_false(self):
        """Network error returns False (not raises)."""
        client = KRXAPIClient(api_key="key", use_mock=False)
        with patch.object(
            client,
            "_make_request",
            side_effect=requests.exceptions.ConnectionError("timeout"),
        ):
            assert client.authenticate() is False


# ============================================================================
# fetch_daily_prices
# ============================================================================


class TestFetchDailyPrices:
    """Tests for KRXAPIClient.fetch_daily_prices()."""

    def test_mock_mode_returns_price_data(self):
        """Mock mode generates PriceData objects."""
        client = KRXAPIClient(use_mock=True)
        prices = client.fetch_daily_prices("2024-01-15")

        assert len(prices) > 0
        assert all(isinstance(p, PriceData) for p in prices)

    def test_mock_mode_all_markets(self):
        """Mock mode returns all 15 stocks for both markets."""
        client = KRXAPIClient(use_mock=True)
        prices = client.fetch_daily_prices("2024-01-15")
        assert len(prices) == 15

    def test_mock_mode_kospi_filter(self):
        """Mock mode with KOSPI filter returns only KOSPI stocks."""
        client = KRXAPIClient(use_mock=True)
        prices = client.fetch_daily_prices("2024-01-15", market=Market.KOSPI)

        assert len(prices) == 10  # 10 KOSPI stocks in mock data
        assert all(p.market == "KOSPI" for p in prices)

    def test_mock_mode_kosdaq_filter(self):
        """Mock mode with KOSDAQ filter returns only KOSDAQ stocks."""
        client = KRXAPIClient(use_mock=True)
        prices = client.fetch_daily_prices("2024-01-15", market=Market.KOSDAQ)

        assert len(prices) == 5  # 5 KOSDAQ stocks in mock data
        assert all(p.market == "KOSDAQ" for p in prices)

    def test_mock_data_deterministic(self):
        """Same date produces same mock data (seeded by date hash)."""
        client = KRXAPIClient(use_mock=True)
        prices1 = client.fetch_daily_prices("2024-01-15")
        prices2 = client.fetch_daily_prices("2024-01-15")

        assert len(prices1) == len(prices2)
        for p1, p2 in zip(prices1, prices2):
            assert p1.close_price == p2.close_price
            assert p1.volume == p2.volume

    def test_invalid_date_format_raises(self):
        """Invalid date format raises ValueError."""
        client = KRXAPIClient(use_mock=True)
        with pytest.raises(ValueError, match="Invalid date format"):
            client.fetch_daily_prices("2024/01/15")

    def test_invalid_date_value_raises(self):
        """Non-existent date raises ValueError."""
        client = KRXAPIClient(use_mock=True)
        with pytest.raises(ValueError, match="Invalid date format"):
            client.fetch_daily_prices("2024-13-01")

    def test_price_data_fields(self):
        """Each PriceData has all expected fields populated."""
        client = KRXAPIClient(use_mock=True)
        prices = client.fetch_daily_prices("2024-01-15")
        sample = prices[0]

        assert sample.stock_code
        assert sample.trade_date == "2024-01-15"
        assert sample.open_price > 0
        assert sample.high_price >= sample.low_price
        assert sample.close_price > 0
        assert sample.volume > 0
        assert sample.trading_value > 0
        assert sample.market_cap > 0
        assert sample.market in ("KOSPI", "KOSDAQ")

    def test_real_mode_calls_make_request(self):
        """Real mode calls _make_request with correct params."""
        client = KRXAPIClient(api_key="key", use_mock=False)
        mock_response = {
            "data": [
                {
                    "stock_code": "005930",
                    "trade_date": "2024-01-15",
                    "open_price": "70000",
                    "high_price": "72000",
                    "low_price": "69000",
                    "close_price": "71000",
                    "volume": "10000000",
                    "trading_value": "710000000000",
                }
            ]
        }
        with patch.object(client, "_make_request", return_value=mock_response) as mock_req:
            prices = client.fetch_daily_prices("2024-01-15", market=Market.KOSPI)

            mock_req.assert_called_once_with(
                endpoint="/data/daily_prices",
                method="GET",
                params={"date": "2024-01-15", "market": "KOSPI"},
            )
            assert len(prices) == 1
            assert prices[0].stock_code == "005930"
            assert prices[0].close_price == 71000.0

    def test_api_failure_propagates(self):
        """API errors in real mode propagate to caller."""
        client = KRXAPIClient(api_key="key", use_mock=False)
        with patch.object(
            client,
            "_make_request",
            side_effect=requests.exceptions.HTTPError("500 Server Error"),
        ):
            with pytest.raises(requests.exceptions.HTTPError):
                client.fetch_daily_prices("2024-01-15")


# ============================================================================
# _transform_response
# ============================================================================


class TestTransformResponse:
    """Tests for KRXAPIClient._transform_response()."""

    def test_valid_records(self):
        """Valid records are transformed to PriceData."""
        client = KRXAPIClient(use_mock=True)
        response = {
            "data": [
                {
                    "stock_code": "005930",
                    "trade_date": "2024-01-15",
                    "open_price": "70000",
                    "high_price": "72000",
                    "low_price": "69000",
                    "close_price": "71000",
                    "volume": "10000000",
                    "trading_value": "710000000000",
                    "market_cap": "430000000000000",
                    "market": "KOSPI",
                }
            ]
        }
        prices = client._transform_response(response)

        assert len(prices) == 1
        p = prices[0]
        assert p.stock_code == "005930"
        assert p.close_price == 71000.0
        assert p.market_cap == 430000000000000.0
        assert p.market == "KOSPI"

    def test_missing_market_cap(self):
        """Record without market_cap sets it to None."""
        client = KRXAPIClient(use_mock=True)
        response = {
            "data": [
                {
                    "stock_code": "005930",
                    "trade_date": "2024-01-15",
                    "open_price": "70000",
                    "high_price": "72000",
                    "low_price": "69000",
                    "close_price": "71000",
                    "volume": "10000000",
                    "trading_value": "710000000000",
                }
            ]
        }
        prices = client._transform_response(response)
        assert prices[0].market_cap is None

    def test_invalid_record_skipped(self):
        """Records with missing required keys are skipped."""
        client = KRXAPIClient(use_mock=True)
        response = {
            "data": [
                {"stock_code": "005930"},  # Missing fields
                {
                    "stock_code": "000660",
                    "trade_date": "2024-01-15",
                    "open_price": "125000",
                    "high_price": "127000",
                    "low_price": "124000",
                    "close_price": "126000",
                    "volume": "5000000",
                    "trading_value": "630000000000",
                },
            ]
        }
        prices = client._transform_response(response)
        assert len(prices) == 1
        assert prices[0].stock_code == "000660"

    def test_empty_data_key(self):
        """Empty 'data' list returns empty result."""
        client = KRXAPIClient(use_mock=True)
        assert client._transform_response({"data": []}) == []

    def test_missing_data_key(self):
        """Missing 'data' key returns empty result."""
        client = KRXAPIClient(use_mock=True)
        assert client._transform_response({}) == []


# ============================================================================
# fetch_market_summary
# ============================================================================


class TestFetchMarketSummary:
    """Tests for KRXAPIClient.fetch_market_summary()."""

    def test_mock_mode_returns_summary(self):
        """Mock mode returns expected market summary dict."""
        client = KRXAPIClient(use_mock=True)
        summary = client.fetch_market_summary("2024-01-15")

        assert summary["date"] == "2024-01-15"
        assert "kospi_index" in summary
        assert "kosdaq_index" in summary
        assert "kospi_volume" in summary
        assert "kosdaq_volume" in summary
        assert "kospi_value" in summary
        assert "kosdaq_value" in summary

    def test_mock_summary_values_reasonable(self):
        """Mock summary values are within reasonable ranges."""
        client = KRXAPIClient(use_mock=True)
        summary = client.fetch_market_summary("2024-01-15")

        assert 1000 < summary["kospi_index"] < 5000
        assert 500 < summary["kosdaq_index"] < 2000

    def test_real_mode_calls_api(self):
        """Real mode calls the correct endpoint."""
        client = KRXAPIClient(api_key="key", use_mock=False)
        mock_response = {"data": {"kospi_index": 2650.5}}
        with patch.object(client, "_make_request", return_value=mock_response) as mock_req:
            summary = client.fetch_market_summary("2024-01-15")

            mock_req.assert_called_once_with(
                endpoint="/data/market_summary",
                method="GET",
                params={"date": "2024-01-15"},
            )
            assert summary == {"kospi_index": 2650.5}


# ============================================================================
# _make_request
# ============================================================================


class TestMakeRequest:
    """Tests for KRXAPIClient._make_request()."""

    def test_unsupported_method_raises(self):
        """Unsupported HTTP method raises ValueError."""
        client = KRXAPIClient(api_key="key", use_mock=True)
        with patch.object(client.rate_limiter, "wait_if_needed"):
            with pytest.raises(ValueError, match="Unsupported HTTP method"):
                client._make_request("/test", method="DELETE")

    def test_get_request_includes_headers(self):
        """GET request includes Authorization and User-Agent headers."""
        client = KRXAPIClient(api_key="my-api-key", use_mock=True)
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}
        mock_response.raise_for_status = MagicMock()

        with patch.object(client.rate_limiter, "wait_if_needed"):
            with patch.object(client.session, "get", return_value=mock_response) as mock_get:
                client._make_request("/test", method="GET", params={"key": "val"})

                call_kwargs = mock_get.call_args
                headers = call_kwargs[1]["headers"]
                assert headers["Authorization"] == "Bearer my-api-key"
                assert headers["User-Agent"] == "ScreenerSystem/1.0"

    def test_post_request_sends_json_body(self):
        """POST request sends data as JSON body."""
        client = KRXAPIClient(api_key="key", use_mock=True)
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "ok"}
        mock_response.raise_for_status = MagicMock()

        with patch.object(client.rate_limiter, "wait_if_needed"):
            with patch.object(client.session, "post", return_value=mock_response) as mock_post:
                client._make_request("/test", method="POST", data={"field": "value"})

                call_kwargs = mock_post.call_args
                assert call_kwargs[1]["json"] == {"field": "value"}

    def test_invalid_json_raises_value_error(self):
        """Non-JSON response raises ValueError."""
        client = KRXAPIClient(api_key="key", use_mock=True)
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.side_effect = ValueError("not json")
        mock_response.text = "not json"

        with patch.object(client.rate_limiter, "wait_if_needed"):
            with patch.object(client.session, "get", return_value=mock_response):
                with pytest.raises(ValueError, match="Invalid JSON response"):
                    client._make_request("/test")


# ============================================================================
# Context Manager and Utilities
# ============================================================================


class TestContextManagerAndUtils:
    """Tests for context manager and create_client()."""

    def test_context_manager(self):
        """Client can be used as context manager."""
        with KRXAPIClient(use_mock=True) as client:
            prices = client.fetch_daily_prices("2024-01-15")
            assert len(prices) > 0

    def test_close(self):
        """close() calls session.close()."""
        client = KRXAPIClient(use_mock=True)
        with patch.object(client.session, "close") as mock_close:
            client.close()
            mock_close.assert_called_once()

    def test_create_client_mock(self):
        """create_client(use_mock=True) returns mock-mode client."""
        client = create_client(use_mock=True)
        assert isinstance(client, KRXAPIClient)
        assert client.use_mock is True

    def test_create_client_default(self, monkeypatch):
        """create_client() reads mock setting from env."""
        monkeypatch.setenv("KRX_USE_MOCK", "true")
        client = create_client()
        assert client.use_mock is True
