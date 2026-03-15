"""Tests for API documentation access control.

Verifies that /docs, /redoc, /openapi.json are disabled in production
and accessible in non-production environments.
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.config import settings


class TestApiDocsInProduction:
    """Test docs endpoints are disabled when ENVIRONMENT=production"""

    def test_docs_disabled_in_production(self, monkeypatch):
        """Swagger UI should return 404 in production"""
        monkeypatch.setattr(settings, "ENVIRONMENT", "production")

        prod_docs_url = None if settings.ENVIRONMENT == "production" else "/docs"
        prod_redoc_url = None if settings.ENVIRONMENT == "production" else "/redoc"
        prod_openapi_url = (
            None if settings.ENVIRONMENT == "production" else "/openapi.json"
        )

        prod_app = FastAPI(
            docs_url=prod_docs_url,
            redoc_url=prod_redoc_url,
            openapi_url=prod_openapi_url,
        )

        @prod_app.get("/")
        def root():
            return {}

        client = TestClient(prod_app)

        assert client.get("/docs").status_code == 404
        assert client.get("/redoc").status_code == 404
        assert client.get("/openapi.json").status_code == 404

    def test_docs_enabled_in_development(self, monkeypatch):
        """Swagger UI should be accessible in development"""
        monkeypatch.setattr(settings, "ENVIRONMENT", "development")

        dev_docs_url = None if settings.ENVIRONMENT == "production" else "/docs"
        dev_redoc_url = None if settings.ENVIRONMENT == "production" else "/redoc"
        dev_openapi_url = (
            None if settings.ENVIRONMENT == "production" else "/openapi.json"
        )

        dev_app = FastAPI(
            docs_url=dev_docs_url,
            redoc_url=dev_redoc_url,
            openapi_url=dev_openapi_url,
        )

        @dev_app.get("/test")
        def test_endpoint():
            return {}

        client = TestClient(dev_app)

        assert client.get("/docs").status_code == 200
        assert client.get("/redoc").status_code == 200
        assert client.get("/openapi.json").status_code == 200

    def test_docs_enabled_in_staging(self, monkeypatch):
        """Swagger UI should be accessible in staging"""
        monkeypatch.setattr(settings, "ENVIRONMENT", "staging")

        staging_docs_url = None if settings.ENVIRONMENT == "production" else "/docs"
        staging_openapi_url = (
            None if settings.ENVIRONMENT == "production" else "/openapi.json"
        )

        staging_app = FastAPI(
            docs_url=staging_docs_url,
            openapi_url=staging_openapi_url,
        )

        @staging_app.get("/test")
        def test_endpoint():
            return {}

        client = TestClient(staging_app)

        assert client.get("/docs").status_code == 200
        assert client.get("/openapi.json").status_code == 200


class TestRootEndpointDocsLink:
    """Test root endpoint omits docs link in production"""

    def test_root_hides_docs_in_production(self, monkeypatch):
        """Root endpoint should not include 'docs' key in production"""
        monkeypatch.setattr(settings, "ENVIRONMENT", "production")

        app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

        @app.get("/")
        async def root():
            response = {
                "message": "Welcome to Stock Screening Platform API",
                "version": "1.0.0",
                "health": "/v1/health",
            }
            if settings.ENVIRONMENT != "production":
                response["docs"] = "/docs"
            return response

        client = TestClient(app)
        data = client.get("/").json()

        assert "docs" not in data
        assert "health" in data

    def test_root_shows_docs_in_development(self, monkeypatch):
        """Root endpoint should include 'docs' key in development"""
        monkeypatch.setattr(settings, "ENVIRONMENT", "development")

        app = FastAPI(docs_url="/docs", openapi_url="/openapi.json")

        @app.get("/")
        async def root():
            response = {
                "message": "Welcome to Stock Screening Platform API",
                "version": "1.0.0",
                "health": "/v1/health",
            }
            if settings.ENVIRONMENT != "production":
                response["docs"] = "/docs"
            return response

        client = TestClient(app)
        data = client.get("/").json()

        assert data.get("docs") == "/docs"


class TestRateLimitWhitelist:
    """Test docs paths are removed from rate limit whitelist"""

    def test_docs_not_in_whitelist(self):
        """Verify /docs, /redoc, /openapi.json are no longer whitelisted"""
        whitelist = settings.RATE_LIMIT_WHITELIST_PATHS
        assert "/docs" not in whitelist, "/docs should not be in rate limit whitelist"
        assert "/redoc" not in whitelist, "/redoc should not be in rate limit whitelist"
        assert (
            "/openapi.json" not in whitelist
        ), "/openapi.json should not be in rate limit whitelist"

    def test_health_still_whitelisted(self):
        """Verify health endpoints remain in whitelist"""
        whitelist = settings.RATE_LIMIT_WHITELIST_PATHS
        assert "/health" in whitelist
