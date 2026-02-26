"""
Tests for KIS API Client.

Covers:
- KISAPIClient initialization and configuration
- get_current_price(): mock data, stock code validation, mocked HTTP response parsing
- get_order_book(): mock data, OrderBook properties (spread, best_bid, best_ask)
- get_chart_data(): mock data, count validation, different period types
- get_stock_info(): mock data for known/unknown stocks
- _make_request(): header construction, rt_cd error detection
- Context manager and utility functions
"""

import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from datetime import datetime, timedelta

from kis_api_client import (
    KISAPIClient,
    CurrentPrice,
    OrderBook,
    OrderBookLevel,
    ChartData,
    StockInfo,
    PriceType,
    TokenBucketRateLimiter,
    CircuitBreaker,
    TokenManager,
    RedisCache,
    create_client,
)


# ============================================================================
# Initialization
# ============================================================================


class TestKISAPIClientInit:
    """Tests for KISAPIClient initialization."""

    def test_mock_mode_explicit(self):
        """Explicit use_mock=True activates mock mode."""
        client = KISAPIClient(use_mock=True)
        assert client.use_mock is True
        assert client.token_manager is None

    def test_mock_mode_auto_no_credentials(self, monkeypatch):
        """Auto-detects mock mode when no credentials are set."""
        monkeypatch.delenv("KIS_APP_KEY", raising=False)
        monkeypatch.delenv("KIS_APP_SECRET", raising=False)
        client = KISAPIClient()
        assert client.use_mock is True

    def test_real_mode_requires_credentials(self):
        """Real mode without credentials raises ValueError."""
        with pytest.raises(ValueError, match="KIS_APP_KEY and KIS_APP_SECRET"):
            KISAPIClient(use_mock=False, app_key=None, app_secret=None)

    def test_virtual_server_default(self):
        """Default server is virtual (paper trading)."""
        client = KISAPIClient(use_mock=True)
        assert "openapivts" in client.base_url

    def test_real_server_url(self, monkeypatch):
        """use_virtual=False selects real server URL."""
        monkeypatch.delenv("KIS_API_BASE_URL_REAL", raising=False)
        client = KISAPIClient(use_mock=True, use_virtual=False)
        assert "openapi.koreainvestment.com" in client.base_url

    def test_rate_limiter_created(self):
        """TokenBucketRateLimiter is initialized."""
        client = KISAPIClient(use_mock=True)
        assert isinstance(client.rate_limiter, TokenBucketRateLimiter)

    def test_circuit_breaker_created(self):
        """CircuitBreaker is initialized."""
        client = KISAPIClient(use_mock=True)
        assert isinstance(client.circuit_breaker, CircuitBreaker)

    def test_cache_disabled_gracefully(self):
        """RedisCache initializes in disabled state without Redis."""
        client = KISAPIClient(use_mock=True, enable_cache=False)
        assert isinstance(client.cache, RedisCache)
        assert client.cache.enabled is False


# ============================================================================
# get_current_price — mock mode
# ============================================================================


class TestGetCurrentPriceMock:
    """Tests for get_current_price() in mock mode."""

    def test_returns_current_price(self):
        """Returns a CurrentPrice dataclass."""
        client = KISAPIClient(use_mock=True)
        price = client.get_current_price("005930")
        assert isinstance(price, CurrentPrice)

    def test_known_stock_name(self):
        """Known stock codes return correct names."""
        client = KISAPIClient(use_mock=True)
        price = client.get_current_price("005930")
        assert price.stock_name == "Samsung Electronics"

    def test_unknown_stock_name_fallback(self):
        """Unknown stock code gets generic name."""
        client = KISAPIClient(use_mock=True)
        price = client.get_current_price("999999")
        assert "999999" in price.stock_name

    def test_price_fields_populated(self):
        """All numeric fields are populated."""
        client = KISAPIClient(use_mock=True)
        price = client.get_current_price("005930")

        assert price.current_price > 0
        assert price.open_price > 0
        assert price.high_price > 0
        assert price.low_price > 0
        assert price.volume > 0
        assert price.trading_value > 0

    def test_deterministic_by_stock_code(self):
        """Same stock code produces same mock data (seeded by code)."""
        client = KISAPIClient(use_mock=True)
        p1 = client.get_current_price("005930")
        p2 = client.get_current_price("005930")
        assert p1.current_price == p2.current_price

    def test_stock_code_matches(self):
        """Returned stock_code matches input."""
        client = KISAPIClient(use_mock=True)
        price = client.get_current_price("000660")
        assert price.stock_code == "000660"


# ============================================================================
# get_current_price — validation
# ============================================================================


class TestGetCurrentPriceValidation:
    """Tests for stock code validation in get_current_price()."""

    def test_empty_code_raises(self):
        """Empty string raises ValueError."""
        client = KISAPIClient(use_mock=True)
        with pytest.raises(ValueError, match="Invalid stock code"):
            client.get_current_price("")

    def test_short_code_raises(self):
        """Less than 6 digits raises ValueError."""
        client = KISAPIClient(use_mock=True)
        with pytest.raises(ValueError, match="Invalid stock code"):
            client.get_current_price("0059")

    def test_long_code_raises(self):
        """More than 6 digits raises ValueError."""
        client = KISAPIClient(use_mock=True)
        with pytest.raises(ValueError, match="Invalid stock code"):
            client.get_current_price("00593001")

    def test_non_digit_code_raises(self):
        """Non-numeric characters raise ValueError."""
        client = KISAPIClient(use_mock=True)
        with pytest.raises(ValueError, match="Invalid stock code"):
            client.get_current_price("ABCDEF")

    def test_none_code_raises(self):
        """None raises ValueError."""
        client = KISAPIClient(use_mock=True)
        with pytest.raises(ValueError, match="Invalid stock code"):
            client.get_current_price(None)


# ============================================================================
# get_current_price — mocked HTTP
# ============================================================================


class TestGetCurrentPriceHTTP:
    """Tests for get_current_price() with mocked API responses."""

    def _make_client_with_mocked_request(self, response_data):
        """Create a non-mock client with _make_request patched."""
        client = KISAPIClient(use_mock=True)
        # Override mock mode to test real parsing path
        client.use_mock = False
        client.token_manager = MagicMock()
        client.token_manager.get_token.return_value = "mock-token"
        client.cache = MagicMock()
        client.cache.get.return_value = None
        client.cache.set.return_value = True

        # Bypass circuit breaker to call function directly
        client.circuit_breaker = MagicMock()
        client.circuit_breaker.call = lambda fn: fn()

        with patch.object(client, "_make_request", return_value=response_data):
            return client

    def test_parses_api_response(self):
        """KIS API response output fields are correctly mapped."""
        response = {
            "rt_cd": "0",
            "output": {
                "hts_kor_isnm": "Samsung Electronics",
                "stck_prpr": "71000",
                "prdy_vrss": "1000",
                "prdy_ctrt": "1.43",
                "stck_oprc": "70000",
                "stck_hgpr": "72000",
                "stck_lwpr": "69500",
                "acml_vol": "15000000",
                "acml_tr_pbmn": "1065000000000",
                "hts_avls": "430000000000000",
            },
        }
        client = KISAPIClient(use_mock=True)
        client.use_mock = False
        client.token_manager = MagicMock()
        client.token_manager.get_token.return_value = "token"
        client.cache = MagicMock()
        client.cache.get.return_value = None
        client.cache.set.return_value = True
        client.circuit_breaker = MagicMock()
        client.circuit_breaker.call = lambda fn: fn()

        with patch.object(client, "_make_request", return_value=response):
            price = client.get_current_price("005930")

        assert price.stock_name == "Samsung Electronics"
        assert price.current_price == 71000.0
        assert price.change_price == 1000.0
        assert price.change_rate == 1.43
        assert price.open_price == 70000.0
        assert price.high_price == 72000.0
        assert price.low_price == 69500.0
        assert price.volume == 15000000
        assert price.market_cap == 430000000000000.0


# ============================================================================
# get_order_book
# ============================================================================


class TestGetOrderBook:
    """Tests for get_order_book() in mock mode."""

    def test_returns_order_book(self):
        """Returns an OrderBook dataclass."""
        client = KISAPIClient(use_mock=True)
        ob = client.get_order_book("005930")
        assert isinstance(ob, OrderBook)

    def test_ten_bid_levels(self):
        """Mock generates 10 bid levels."""
        client = KISAPIClient(use_mock=True)
        ob = client.get_order_book("005930")
        assert len(ob.bid_levels) == 10

    def test_ten_ask_levels(self):
        """Mock generates 10 ask levels."""
        client = KISAPIClient(use_mock=True)
        ob = client.get_order_book("005930")
        assert len(ob.ask_levels) == 10

    def test_bid_ask_level_type(self):
        """Bid and ask levels are OrderBookLevel instances."""
        client = KISAPIClient(use_mock=True)
        ob = client.get_order_book("005930")
        assert isinstance(ob.bid_levels[0], OrderBookLevel)
        assert isinstance(ob.ask_levels[0], OrderBookLevel)

    def test_spread_positive(self):
        """Spread (best_ask - best_bid) is positive."""
        client = KISAPIClient(use_mock=True)
        ob = client.get_order_book("005930")
        assert ob.spread > 0

    def test_best_bid_is_highest_bid(self):
        """best_bid is the first (highest) bid level price."""
        client = KISAPIClient(use_mock=True)
        ob = client.get_order_book("005930")
        assert ob.best_bid == ob.bid_levels[0].price

    def test_best_ask_is_lowest_ask(self):
        """best_ask is the first (lowest) ask level price."""
        client = KISAPIClient(use_mock=True)
        ob = client.get_order_book("005930")
        assert ob.best_ask == ob.ask_levels[0].price

    def test_total_volumes(self):
        """Total volumes match sum of individual levels."""
        client = KISAPIClient(use_mock=True)
        ob = client.get_order_book("005930")
        assert ob.total_bid_volume == sum(l.volume for l in ob.bid_levels)
        assert ob.total_ask_volume == sum(l.volume for l in ob.ask_levels)

    def test_bid_prices_descending(self):
        """Bid prices are in descending order (best to worst)."""
        client = KISAPIClient(use_mock=True)
        ob = client.get_order_book("005930")
        for i in range(len(ob.bid_levels) - 1):
            assert ob.bid_levels[i].price > ob.bid_levels[i + 1].price

    def test_ask_prices_ascending(self):
        """Ask prices are in ascending order (best to worst)."""
        client = KISAPIClient(use_mock=True)
        ob = client.get_order_book("005930")
        for i in range(len(ob.ask_levels) - 1):
            assert ob.ask_levels[i].price < ob.ask_levels[i + 1].price

    def test_invalid_code_raises(self):
        """Invalid stock code raises ValueError."""
        client = KISAPIClient(use_mock=True)
        with pytest.raises(ValueError, match="Invalid stock code"):
            client.get_order_book("ABC")


# ============================================================================
# get_chart_data
# ============================================================================


class TestGetChartData:
    """Tests for get_chart_data() in mock mode."""

    def test_returns_chart_data_list(self):
        """Returns list of ChartData objects."""
        client = KISAPIClient(use_mock=True)
        chart = client.get_chart_data("005930", PriceType.DAILY, 10)
        assert isinstance(chart, list)
        assert all(isinstance(c, ChartData) for c in chart)

    def test_correct_count(self):
        """Returns exactly the requested number of candles."""
        client = KISAPIClient(use_mock=True)
        chart = client.get_chart_data("005930", PriceType.DAILY, 30)
        assert len(chart) == 30

    def test_count_below_1_raises(self):
        """Count < 1 raises ValueError."""
        client = KISAPIClient(use_mock=True)
        with pytest.raises(ValueError, match="Count must be between 1 and 100"):
            client.get_chart_data("005930", PriceType.DAILY, 0)

    def test_count_above_100_raises(self):
        """Count > 100 raises ValueError."""
        client = KISAPIClient(use_mock=True)
        with pytest.raises(ValueError, match="Count must be between 1 and 100"):
            client.get_chart_data("005930", PriceType.DAILY, 101)

    def test_daily_period_dates(self):
        """Daily period generates YYYYMMDD format dates."""
        client = KISAPIClient(use_mock=True)
        chart = client.get_chart_data("005930", PriceType.DAILY, 5)
        for candle in chart:
            assert len(candle.date) == 8
            assert candle.date.isdigit()

    def test_minute_period_dates(self):
        """Minute period generates YYYYMMDDHHmmSS format dates."""
        client = KISAPIClient(use_mock=True)
        chart = client.get_chart_data("005930", PriceType.MINUTE_1, 5)
        for candle in chart:
            assert len(candle.date) == 14
            assert candle.date.isdigit()

    def test_ohlcv_values_reasonable(self):
        """OHLCV values are positive and high >= low."""
        client = KISAPIClient(use_mock=True)
        chart = client.get_chart_data("005930", PriceType.DAILY, 10)
        for candle in chart:
            assert candle.open_price > 0
            assert candle.high_price >= candle.low_price
            assert candle.close_price > 0
            assert candle.volume > 0

    def test_trading_value_present(self):
        """Mock chart data includes trading_value."""
        client = KISAPIClient(use_mock=True)
        chart = client.get_chart_data("005930", PriceType.DAILY, 5)
        for candle in chart:
            assert candle.trading_value is not None
            assert candle.trading_value > 0

    def test_stock_code_in_chart_data(self):
        """Each ChartData has the correct stock_code."""
        client = KISAPIClient(use_mock=True)
        chart = client.get_chart_data("000660", PriceType.DAILY, 5)
        for candle in chart:
            assert candle.stock_code == "000660"

    def test_invalid_code_raises(self):
        """Invalid stock code raises ValueError."""
        client = KISAPIClient(use_mock=True)
        with pytest.raises(ValueError, match="Invalid stock code"):
            client.get_chart_data("XYZ", PriceType.DAILY, 10)


# ============================================================================
# get_stock_info
# ============================================================================


class TestGetStockInfo:
    """Tests for get_stock_info() in mock mode."""

    def test_known_stock_returns_info(self):
        """Known stock returns populated StockInfo."""
        client = KISAPIClient(use_mock=True)
        info = client.get_stock_info("005930")

        assert isinstance(info, StockInfo)
        assert info.stock_name == "Samsung Electronics"
        assert info.market == "KOSPI"
        assert info.sector == "Technology"
        assert info.industry == "Semiconductor"

    def test_unknown_stock_fallback(self):
        """Unknown stock gets default values."""
        client = KISAPIClient(use_mock=True)
        info = client.get_stock_info("123456")

        assert info.stock_code == "123456"
        assert "123456" in info.stock_name
        assert info.market == "KOSPI"

    def test_listed_shares_and_face_value(self):
        """Mock always provides listed_shares and face_value."""
        client = KISAPIClient(use_mock=True)
        info = client.get_stock_info("005930")
        assert info.listed_shares == 1000000000
        assert info.face_value == 100.0

    def test_all_known_stocks(self):
        """All five known stocks return correct names."""
        client = KISAPIClient(use_mock=True)
        known_stocks = {
            "005930": "Samsung Electronics",
            "000660": "SK Hynix",
            "035420": "NAVER",
            "051910": "LG Chem",
            "035720": "Kakao",
        }
        for code, expected_name in known_stocks.items():
            info = client.get_stock_info(code)
            assert info.stock_name == expected_name

    def test_invalid_code_raises(self):
        """Invalid stock code raises ValueError."""
        client = KISAPIClient(use_mock=True)
        with pytest.raises(ValueError, match="Invalid stock code"):
            client.get_stock_info("short")


# ============================================================================
# _make_request
# ============================================================================


class TestKISMakeRequest:
    """Tests for KISAPIClient._make_request()."""

    def _make_client(self):
        """Create client with mocked internals for _make_request testing."""
        client = KISAPIClient(use_mock=True)
        client.use_mock = False
        client.token_manager = MagicMock()
        client.token_manager.get_token.return_value = "test-token"
        client.app_key = "test-key"
        client.app_secret = "test-secret"
        return client

    def test_request_includes_tr_id_header(self):
        """Request headers include tr_id."""
        client = self._make_client()
        mock_response = MagicMock()
        mock_response.json.return_value = {"rt_cd": "0", "output": {}}
        mock_response.raise_for_status = MagicMock()

        with patch.object(client.rate_limiter, "wait_if_needed"):
            with patch.object(client.session, "get", return_value=mock_response) as mock_get:
                client._make_request("/test", "FHKST01010100", {"key": "val"})

                headers = mock_get.call_args[1]["headers"]
                assert headers["tr_id"] == "FHKST01010100"
                assert headers["authorization"] == "Bearer test-token"
                assert headers["appkey"] == "test-key"
                assert headers["appsecret"] == "test-secret"
                assert headers["custtype"] == "P"

    def test_api_error_rt_cd_raises(self):
        """Non-zero rt_cd raises ValueError."""
        client = self._make_client()
        mock_response = MagicMock()
        mock_response.json.return_value = {"rt_cd": "1", "msg1": "Error occurred"}
        mock_response.raise_for_status = MagicMock()

        with patch.object(client.rate_limiter, "wait_if_needed"):
            with patch.object(client.session, "get", return_value=mock_response):
                with pytest.raises(ValueError, match="KIS API error"):
                    client._make_request("/test", "TR001")

    def test_success_returns_data(self):
        """Successful response returns JSON data."""
        client = self._make_client()
        expected = {"rt_cd": "0", "output": {"price": "70000"}}
        mock_response = MagicMock()
        mock_response.json.return_value = expected
        mock_response.raise_for_status = MagicMock()

        with patch.object(client.rate_limiter, "wait_if_needed"):
            with patch.object(client.session, "get", return_value=mock_response):
                result = client._make_request("/test", "TR001")
                assert result == expected


# ============================================================================
# OrderBook properties
# ============================================================================


class TestOrderBookProperties:
    """Tests for OrderBook computed properties."""

    def test_spread_calculation(self):
        """Spread is ask[0] - bid[0]."""
        ob = OrderBook(
            stock_code="005930",
            stock_name="Test",
            bid_levels=[OrderBookLevel(70000, 100, 10)],
            ask_levels=[OrderBookLevel(70100, 200, 20)],
            total_bid_volume=100,
            total_ask_volume=200,
        )
        assert ob.spread == 100.0

    def test_spread_empty_levels(self):
        """Spread is 0.0 when bid or ask is empty."""
        ob = OrderBook(
            stock_code="005930",
            stock_name="Test",
            bid_levels=[],
            ask_levels=[],
            total_bid_volume=0,
            total_ask_volume=0,
        )
        assert ob.spread == 0.0

    def test_best_bid_none_when_empty(self):
        """best_bid is None when no bid levels."""
        ob = OrderBook(
            stock_code="005930",
            stock_name="Test",
            bid_levels=[],
            ask_levels=[OrderBookLevel(70100, 200, 20)],
            total_bid_volume=0,
            total_ask_volume=200,
        )
        assert ob.best_bid is None

    def test_best_ask_none_when_empty(self):
        """best_ask is None when no ask levels."""
        ob = OrderBook(
            stock_code="005930",
            stock_name="Test",
            bid_levels=[OrderBookLevel(70000, 100, 10)],
            ask_levels=[],
            total_bid_volume=100,
            total_ask_volume=0,
        )
        assert ob.best_ask is None


# ============================================================================
# Context Manager and Utilities
# ============================================================================


class TestKISContextManagerAndUtils:
    """Tests for context manager and create_client()."""

    def test_context_manager(self):
        """Client can be used as context manager."""
        with KISAPIClient(use_mock=True) as client:
            price = client.get_current_price("005930")
            assert isinstance(price, CurrentPrice)

    def test_close(self):
        """close() calls session.close()."""
        client = KISAPIClient(use_mock=True)
        with patch.object(client.session, "close") as mock_close:
            client.close()
            mock_close.assert_called_once()

    def test_create_client_mock(self):
        """create_client(use_mock=True) returns mock-mode client."""
        client = create_client(use_mock=True)
        assert isinstance(client, KISAPIClient)
        assert client.use_mock is True

    def test_create_client_auto_mock(self, monkeypatch):
        """create_client() auto-detects mock mode without credentials."""
        monkeypatch.delenv("KIS_APP_KEY", raising=False)
        monkeypatch.delenv("KIS_APP_SECRET", raising=False)
        client = create_client()
        assert client.use_mock is True
