"""
Tests for data pipeline utility classes.

Covers:
- RateLimiter (KRX): sliding window rate limiting
- TokenBucketRateLimiter (KIS): token bucket algorithm
- CircuitBreaker: fault tolerance state machine
- TokenManager: OAuth 2.0 token lifecycle
"""

import time
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from krx_api_client import RateLimiter
from kis_api_client import TokenBucketRateLimiter, CircuitBreaker, TokenManager


# ============================================================================
# RateLimiter (KRX)
# ============================================================================


class TestRateLimiter:
    """Tests for KRX sliding window rate limiter."""

    def test_default_limits(self):
        """Default limits are 10/s and 1000/h."""
        rl = RateLimiter()
        assert rl.calls_per_second == 10
        assert rl.calls_per_hour == 1000

    def test_custom_limits(self):
        """Custom limits are accepted."""
        rl = RateLimiter(calls_per_second=5, calls_per_hour=500)
        assert rl.calls_per_second == 5
        assert rl.calls_per_hour == 500

    def test_starts_empty(self):
        """Call lists start empty."""
        rl = RateLimiter()
        assert rl.second_calls == []
        assert rl.hour_calls == []

    def test_single_call_records_timestamps(self):
        """A single call records timestamps in both lists."""
        rl = RateLimiter()
        rl.wait_if_needed()
        assert len(rl.second_calls) == 1
        assert len(rl.hour_calls) == 1

    def test_calls_within_limit_no_sleep(self):
        """Calls within the per-second limit do not sleep."""
        rl = RateLimiter(calls_per_second=5)

        with patch("krx_api_client.time.sleep") as mock_sleep:
            for _ in range(4):
                rl.wait_if_needed()
            mock_sleep.assert_not_called()

    @patch("krx_api_client.time.sleep")
    def test_exceeding_per_second_limit_sleeps(self, mock_sleep):
        """Exceeding per-second limit triggers sleep."""
        rl = RateLimiter(calls_per_second=2)

        # First 2 calls are fine
        rl.wait_if_needed()
        rl.wait_if_needed()

        # 3rd call should trigger sleep
        rl.wait_if_needed()
        assert mock_sleep.called

    def test_old_calls_cleaned_up(self):
        """Calls older than 1 second are removed from second_calls."""
        rl = RateLimiter(calls_per_second=10)
        # Simulate an old call 2 seconds ago
        rl.second_calls = [time.time() - 2.0]
        rl.hour_calls = [time.time() - 2.0]

        rl.wait_if_needed()

        # Old call should be cleaned, only the new one remains
        assert len(rl.second_calls) == 1


# ============================================================================
# TokenBucketRateLimiter (KIS)
# ============================================================================


class TestTokenBucketRateLimiter:
    """Tests for KIS token bucket rate limiter."""

    def test_default_rate(self):
        """Default rate is 20 requests/second."""
        rl = TokenBucketRateLimiter()
        assert rl.rate == 20
        assert rl.per == 1.0

    def test_custom_rate(self):
        """Custom rate is accepted."""
        rl = TokenBucketRateLimiter(rate=10, per=2.0)
        assert rl.rate == 10
        assert rl.per == 2.0

    def test_initial_allowance_equals_rate(self):
        """Initial token allowance equals the configured rate."""
        rl = TokenBucketRateLimiter(rate=15)
        assert rl.allowance == 15.0

    def test_single_call_decrements_allowance(self):
        """A single call decrements allowance by ~1."""
        rl = TokenBucketRateLimiter(rate=20)
        initial = rl.allowance
        rl.wait_if_needed()
        # Allowance should decrease (accounting for small time-based replenishment)
        assert rl.allowance < initial

    @patch("kis_api_client.time.sleep")
    def test_exhausted_tokens_trigger_sleep(self, mock_sleep):
        """When tokens are exhausted, sleep is triggered."""
        rl = TokenBucketRateLimiter(rate=2, per=1.0)
        rl.allowance = 0.0
        rl.last_check = time.time()

        rl.wait_if_needed()
        mock_sleep.assert_called_once()

    def test_allowance_capped_at_rate(self):
        """Token allowance never exceeds the configured rate."""
        rl = TokenBucketRateLimiter(rate=5)
        # Simulate time passing to accumulate tokens
        rl.last_check = time.time() - 10.0
        rl.wait_if_needed()
        # After replenishment + consumption, allowance should be <= rate
        assert rl.allowance <= rl.rate


# ============================================================================
# CircuitBreaker
# ============================================================================


class TestCircuitBreaker:
    """Tests for circuit breaker fault tolerance pattern."""

    def test_initial_state_closed(self):
        """Circuit starts in CLOSED state."""
        cb = CircuitBreaker()
        assert cb.state == "CLOSED"
        assert cb.failure_count == 0

    def test_successful_call_returns_result(self):
        """Successful function call returns the function result."""
        cb = CircuitBreaker()
        result = cb.call(lambda: 42)
        assert result == 42

    def test_successful_call_keeps_closed(self):
        """Successful calls keep circuit CLOSED."""
        cb = CircuitBreaker(failure_threshold=3)
        cb.call(lambda: "ok")
        assert cb.state == "CLOSED"
        assert cb.failure_count == 0

    def test_failure_increments_count(self):
        """Failed calls increment failure counter."""
        cb = CircuitBreaker(failure_threshold=5)

        with pytest.raises(ValueError):
            cb.call(self._raise_value_error)

        assert cb.failure_count == 1
        assert cb.state == "CLOSED"

    def test_reaching_threshold_opens_circuit(self):
        """Reaching failure threshold transitions to OPEN."""
        cb = CircuitBreaker(failure_threshold=3)

        for _ in range(3):
            with pytest.raises(ValueError):
                cb.call(self._raise_value_error)

        assert cb.state == "OPEN"
        assert cb.failure_count == 3

    def test_open_circuit_rejects_calls(self):
        """OPEN circuit rejects calls without executing the function."""
        cb = CircuitBreaker(failure_threshold=2, timeout=60)

        # Open the circuit
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(self._raise_value_error)

        # Next call should be rejected by the circuit breaker itself
        with pytest.raises(Exception, match="Circuit breaker OPEN"):
            cb.call(lambda: "should not execute")

    def test_timeout_transitions_to_half_open(self):
        """After timeout, circuit transitions from OPEN to HALF_OPEN."""
        cb = CircuitBreaker(failure_threshold=2, timeout=1)

        # Open the circuit
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(self._raise_value_error)
        assert cb.state == "OPEN"

        # Simulate timeout expiration
        cb.last_failure_time = time.time() - 2

        # Next call should be allowed (HALF_OPEN)
        result = cb.call(lambda: "recovered")
        assert result == "recovered"
        assert cb.state == "CLOSED"

    def test_half_open_success_closes_circuit(self):
        """Successful call in HALF_OPEN transitions to CLOSED."""
        cb = CircuitBreaker(failure_threshold=2, timeout=1)

        # Open the circuit
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(self._raise_value_error)

        # Simulate timeout
        cb.last_failure_time = time.time() - 2

        # Successful call in HALF_OPEN
        cb.call(lambda: "ok")
        assert cb.state == "CLOSED"
        assert cb.failure_count == 0

    def test_half_open_failure_reopens_circuit(self):
        """Failed call in HALF_OPEN transitions back to OPEN."""
        cb = CircuitBreaker(failure_threshold=2, timeout=1)

        # Open the circuit
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(self._raise_value_error)

        # Simulate timeout
        cb.last_failure_time = time.time() - 2

        # Failed call in HALF_OPEN — should reopen
        with pytest.raises(ValueError):
            cb.call(self._raise_value_error)

        assert cb.state == "OPEN"

    def test_success_after_failures_resets_count(self):
        """A successful call resets the failure counter."""
        cb = CircuitBreaker(failure_threshold=5)

        # Accumulate some failures
        for _ in range(3):
            with pytest.raises(ValueError):
                cb.call(self._raise_value_error)
        assert cb.failure_count == 3

        # Successful call resets
        cb.call(lambda: "ok")
        assert cb.failure_count == 0

    def test_default_parameters(self):
        """Default parameters are failure_threshold=5, timeout=60."""
        cb = CircuitBreaker()
        assert cb.failure_threshold == 5
        assert cb.timeout == 60

    @staticmethod
    def _raise_value_error():
        raise ValueError("test error")


# ============================================================================
# TokenManager
# ============================================================================


class TestTokenManager:
    """Tests for OAuth 2.0 token lifecycle management."""

    def test_initialization(self):
        """Token manager initializes with empty token state."""
        tm = TokenManager(
            app_key="test_key",
            app_secret="test_secret",
            base_url="https://api.example.com",
        )
        assert tm.access_token is None
        assert tm.token_type is None
        assert tm.expires_at is None

    def test_needs_refresh_when_no_token(self):
        """Refresh needed when no token exists."""
        tm = TokenManager("key", "secret", "https://api.example.com")
        assert tm._needs_refresh() is True

    def test_needs_refresh_when_no_expiry(self):
        """Refresh needed when expiry time not set."""
        tm = TokenManager("key", "secret", "https://api.example.com")
        tm.access_token = "some_token"
        tm.expires_at = None
        assert tm._needs_refresh() is True

    def test_no_refresh_when_valid(self):
        """No refresh needed when token is valid and not near expiry."""
        tm = TokenManager("key", "secret", "https://api.example.com")
        tm.access_token = "valid_token"
        tm.expires_at = datetime.now() + timedelta(hours=1)
        assert tm._needs_refresh() is False

    def test_needs_refresh_near_expiry(self):
        """Refresh needed when within 5 minutes of expiry."""
        tm = TokenManager("key", "secret", "https://api.example.com")
        tm.access_token = "expiring_token"
        # 3 minutes from now — within 5-minute buffer
        tm.expires_at = datetime.now() + timedelta(minutes=3)
        assert tm._needs_refresh() is True

    def test_no_refresh_just_outside_buffer(self):
        """No refresh needed when token expires in 6 minutes (outside 5-min buffer)."""
        tm = TokenManager("key", "secret", "https://api.example.com")
        tm.access_token = "valid_token"
        tm.expires_at = datetime.now() + timedelta(minutes=6)
        assert tm._needs_refresh() is False

    @patch("kis_api_client.requests.post")
    def test_get_token_refreshes_when_needed(self, mock_post):
        """get_token() triggers refresh and returns new token."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "new_token_abc",
            "token_type": "Bearer",
            "expires_in": 86400,
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        tm = TokenManager("key", "secret", "https://api.example.com")
        token = tm.get_token()

        assert token == "new_token_abc"
        assert tm.access_token == "new_token_abc"
        assert tm.token_type == "Bearer"
        assert tm.expires_at is not None
        mock_post.assert_called_once()

    @patch("kis_api_client.requests.post")
    def test_get_token_uses_cached_when_valid(self, mock_post):
        """get_token() returns cached token without calling API."""
        tm = TokenManager("key", "secret", "https://api.example.com")
        tm.access_token = "cached_token"
        tm.token_type = "Bearer"
        tm.expires_at = datetime.now() + timedelta(hours=1)

        token = tm.get_token()

        assert token == "cached_token"
        mock_post.assert_not_called()

    @patch("kis_api_client.requests.post")
    def test_refresh_sets_default_expiry(self, mock_post):
        """Refresh uses 24h default when expires_in not provided."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "token_no_expiry",
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        tm = TokenManager("key", "secret", "https://api.example.com")
        tm._refresh_token()

        assert tm.access_token == "token_no_expiry"
        # Default expiry should be ~24 hours from now
        time_diff = tm.expires_at - datetime.now()
        assert timedelta(hours=23) < time_diff < timedelta(hours=25)

    @patch("kis_api_client.requests.post")
    def test_refresh_failure_raises(self, mock_post):
        """HTTP failure during refresh propagates the exception."""
        import requests as req

        mock_post.side_effect = req.exceptions.ConnectionError("Network error")

        tm = TokenManager("key", "secret", "https://api.example.com")

        with pytest.raises(req.exceptions.ConnectionError):
            tm._refresh_token()

    @patch("kis_api_client.requests.post")
    def test_refresh_invalid_response_raises(self, mock_post):
        """Missing access_token in response raises ValueError."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"error": "invalid_grant"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        tm = TokenManager("key", "secret", "https://api.example.com")

        with pytest.raises((KeyError, ValueError)):
            tm._refresh_token()
