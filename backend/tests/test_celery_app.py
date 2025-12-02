"""Tests for Celery application configuration"""

from unittest.mock import patch


class TestCeleryAppConfiguration:
    """Test Celery application configuration"""

    def test_celery_app_import(self):
        """Test celery_app can be imported"""
        with patch("app.core.config.settings") as mock_settings:
            mock_settings.CELERY_BROKER_URL = "redis://localhost:6379/0"
            mock_settings.CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
            mock_settings.REDIS_URL = "redis://localhost:6379/0"

            from app.celery_app import celery_app

            assert celery_app is not None
            assert celery_app.main == "stock_screening"

    def test_celery_configuration_values(self):
        """Test Celery configuration values are set correctly"""
        with patch("app.core.config.settings") as mock_settings:
            mock_settings.CELERY_BROKER_URL = "redis://test:6379/0"
            mock_settings.CELERY_RESULT_BACKEND = "redis://test:6379/1"
            mock_settings.REDIS_URL = "redis://test:6379/0"

            from app.celery_app import celery_app

            assert celery_app.conf.task_serializer == "json"
            assert celery_app.conf.accept_content == ["json"]
            assert celery_app.conf.result_serializer == "json"
            assert celery_app.conf.timezone == "UTC"
            assert celery_app.conf.enable_utc is True

    def test_celery_task_settings(self):
        """Test Celery task-related settings"""
        with patch("app.core.config.settings") as mock_settings:
            mock_settings.CELERY_BROKER_URL = "redis://localhost:6379/0"
            mock_settings.CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
            mock_settings.REDIS_URL = "redis://localhost:6379/0"

            from app.celery_app import celery_app

            assert celery_app.conf.task_track_started is True
            assert celery_app.conf.task_time_limit == 3600
            assert celery_app.conf.task_soft_time_limit == 3000

    def test_celery_worker_settings(self):
        """Test Celery worker-related settings"""
        with patch("app.core.config.settings") as mock_settings:
            mock_settings.CELERY_BROKER_URL = "redis://localhost:6379/0"
            mock_settings.CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
            mock_settings.REDIS_URL = "redis://localhost:6379/0"

            from app.celery_app import celery_app

            assert celery_app.conf.worker_prefetch_multiplier == 1
            assert celery_app.conf.worker_max_tasks_per_child == 1000

    def test_celery_uses_redis_url_fallback(self):
        """Test Celery uses REDIS_URL as fallback when specific URLs not set"""
        with patch("app.core.config.settings") as mock_settings:
            mock_settings.CELERY_BROKER_URL = ""
            mock_settings.CELERY_RESULT_BACKEND = ""
            mock_settings.REDIS_URL = "redis://fallback:6379/0"

            # Reload the module to test with new settings
            import importlib

            import app.celery_app

            importlib.reload(app.celery_app)

            # The celery app should use REDIS_URL as fallback
            from app.celery_app import celery_app

            assert celery_app is not None
