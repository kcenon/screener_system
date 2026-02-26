"""
Tests for DataSourceFactory and source type detection.

Covers:
- DataSourceFactory._detect_source_type(): env-based auto-detection
- DataSourceFactory.create(): factory instantiation with fallback logic
"""

import pytest
from unittest.mock import patch, MagicMock

from data_source import DataSourceFactory, DataSourceType, MockDataSource, KISDataSource


# ============================================================================
# DataSourceFactory._detect_source_type
# ============================================================================


class TestDetectSourceType:
    """Tests for environment-based data source detection."""

    @patch.dict("os.environ", {"DATA_SOURCE_TYPE": "kis"}, clear=False)
    def test_explicit_kis(self):
        """Explicit 'kis' env var returns KIS type."""
        result = DataSourceFactory._detect_source_type()
        assert result == DataSourceType.KIS

    @patch.dict("os.environ", {"DATA_SOURCE_TYPE": "krx"}, clear=False)
    def test_explicit_krx(self):
        """Explicit 'krx' env var returns KRX type."""
        result = DataSourceFactory._detect_source_type()
        assert result == DataSourceType.KRX

    @patch.dict("os.environ", {"DATA_SOURCE_TYPE": "mock"}, clear=False)
    def test_explicit_mock(self):
        """Explicit 'mock' env var returns MOCK type."""
        result = DataSourceFactory._detect_source_type()
        assert result == DataSourceType.MOCK

    @patch.dict("os.environ", {"DATA_SOURCE_TYPE": "KIS"}, clear=False)
    def test_case_insensitive(self):
        """Detection is case-insensitive."""
        result = DataSourceFactory._detect_source_type()
        assert result == DataSourceType.KIS

    @patch.dict(
        "os.environ",
        {"KIS_APP_KEY": "test_key", "KIS_APP_SECRET": "test_secret"},
        clear=False,
    )
    def test_auto_detect_kis_credentials(self):
        """Auto-detects KIS when credentials are present and no explicit type."""
        # Remove DATA_SOURCE_TYPE if it exists
        with patch.dict("os.environ", {}, clear=False):
            import os
            os.environ.pop("DATA_SOURCE_TYPE", None)
            result = DataSourceFactory._detect_source_type()
        assert result == DataSourceType.KIS

    def test_defaults_to_mock_no_credentials(self):
        """Defaults to MOCK when no credentials and no explicit type."""
        env = {
            "DATA_SOURCE_TYPE": "",
        }
        with patch.dict("os.environ", env, clear=False):
            import os
            os.environ.pop("KIS_APP_KEY", None)
            os.environ.pop("KIS_APP_SECRET", None)
            result = DataSourceFactory._detect_source_type()
        assert result == DataSourceType.MOCK

    @patch.dict(
        "os.environ",
        {"DATA_SOURCE_TYPE": "unknown_value"},
        clear=False,
    )
    def test_unknown_explicit_type_defaults_to_mock(self):
        """Unknown explicit type with no KIS credentials defaults to MOCK."""
        with patch.dict("os.environ", {}, clear=False):
            import os
            os.environ.pop("KIS_APP_KEY", None)
            os.environ.pop("KIS_APP_SECRET", None)
            result = DataSourceFactory._detect_source_type()
        assert result == DataSourceType.MOCK


# ============================================================================
# DataSourceFactory.create
# ============================================================================


class TestDataSourceFactoryCreate:
    """Tests for factory data source creation."""

    def test_create_mock_explicit(self):
        """Explicit MOCK type creates MockDataSource."""
        source = DataSourceFactory.create(DataSourceType.MOCK)
        assert isinstance(source, MockDataSource)

    def test_create_kis_without_credentials_falls_back_to_mock(self):
        """KIS type without credentials falls back to MockDataSource."""
        with patch.dict("os.environ", {}, clear=False):
            import os
            os.environ.pop("KIS_APP_KEY", None)
            os.environ.pop("KIS_APP_SECRET", None)
            source = DataSourceFactory.create(DataSourceType.KIS)
        assert isinstance(source, MockDataSource)

    def test_create_kis_with_credentials(self):
        """KIS type with credentials creates KISDataSource."""
        env = {
            "KIS_APP_KEY": "test_app_key",
            "KIS_APP_SECRET": "test_app_secret",
            "KIS_USE_VIRTUAL_SERVER": "true",
        }
        with patch.dict("os.environ", env, clear=False):
            with patch("data_source.KISAPIClient") as mock_client:
                source = DataSourceFactory.create(DataSourceType.KIS)
        assert isinstance(source, KISDataSource)

    def test_create_krx_raises_not_implemented(self):
        """KRX type raises NotImplementedError."""
        with pytest.raises(NotImplementedError, match="KRX data source not yet implemented"):
            DataSourceFactory.create(DataSourceType.KRX)

    def test_create_auto_detect_mock(self):
        """Auto-detect with no credentials creates MockDataSource."""
        with patch.dict("os.environ", {"DATA_SOURCE_TYPE": ""}, clear=False):
            import os
            os.environ.pop("KIS_APP_KEY", None)
            os.environ.pop("KIS_APP_SECRET", None)
            source = DataSourceFactory.create()
        assert isinstance(source, MockDataSource)

    def test_create_kis_virtual_server_flag(self):
        """KIS creation respects KIS_USE_VIRTUAL_SERVER setting."""
        env = {
            "KIS_APP_KEY": "key",
            "KIS_APP_SECRET": "secret",
            "KIS_USE_VIRTUAL_SERVER": "false",
        }
        with patch.dict("os.environ", env, clear=False):
            with patch("data_source.KISAPIClient") as mock_client:
                source = DataSourceFactory.create(DataSourceType.KIS)
                # Verify use_virtual=False was passed
                mock_client.assert_called_once()
                call_kwargs = mock_client.call_args
                assert call_kwargs[1].get("use_virtual") is False or \
                    (len(call_kwargs[0]) >= 3 and call_kwargs[0][2] is False)

    def test_mock_source_is_context_manager(self):
        """MockDataSource supports context manager protocol."""
        source = DataSourceFactory.create(DataSourceType.MOCK)
        assert hasattr(source, "__enter__")
        assert hasattr(source, "__exit__")
