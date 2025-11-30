"""Unit tests for custom exception handling.

This module tests the custom exception classes and error handling infrastructure
to ensure consistent error responses across the API.

Test Coverage:
    - Custom exception class initialization and attributes
    - HTTP status codes for each exception type
    - Error response format consistency
    - Exception handler integration with FastAPI
    - Security (no sensitive information in error responses)
"""

import pytest
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from pydantic import BaseModel, field_validator
from sqlalchemy.exc import SQLAlchemyError

from app.api.error_handlers import (
    app_exception_handler,
    generic_exception_handler,
    sqlalchemy_exception_handler,
    validation_exception_handler,
)
from app.core.exceptions import (
    AppException,
    BadRequestException,
    CacheException,
    ConflictException,
    DatabaseException,
    ExternalAPIException,
    ForbiddenException,
    NotFoundException,
    RateLimitException,
    UnauthorizedException,
    ValidationException,
)


# ============================================================================
# TEST FIXTURES
# ============================================================================


@pytest.fixture
def test_app():
    """Create a test FastAPI application with exception handlers registered."""
    app = FastAPI(debug=False)

    # Register exception handlers
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # Test routes that raise exceptions
    @app.get("/test/app-exception")
    async def raise_app_exception():
        raise AppException(
            "Test app exception", status_code=500, detail={"key": "value"}
        )

    @app.get("/test/not-found")
    async def raise_not_found():
        raise NotFoundException("Resource not found")

    @app.get("/test/unauthorized")
    async def raise_unauthorized():
        raise UnauthorizedException("Invalid credentials")

    @app.get("/test/forbidden")
    async def raise_forbidden():
        raise ForbiddenException("Access denied")

    @app.get("/test/bad-request")
    async def raise_bad_request():
        raise BadRequestException("Invalid request")

    @app.get("/test/conflict")
    async def raise_conflict():
        raise ConflictException("Resource already exists")

    @app.get("/test/validation")
    async def raise_validation():
        raise ValidationException("Validation failed")

    @app.get("/test/rate-limit")
    async def raise_rate_limit():
        raise RateLimitException("Too many requests")

    @app.get("/test/external-api")
    async def raise_external_api():
        raise ExternalAPIException("External service unavailable")

    @app.get("/test/database")
    async def raise_database():
        raise DatabaseException("Database connection failed")

    @app.get("/test/cache")
    async def raise_cache():
        raise CacheException("Cache operation failed")

    @app.get("/test/generic")
    async def raise_generic():
        raise ValueError("Unexpected error")

    @app.get("/test/sqlalchemy")
    async def raise_sqlalchemy():
        raise SQLAlchemyError("Database query failed")

    # Route with Pydantic validation
    class TestModel(BaseModel):
        name: str
        age: int

        @field_validator("age")
        @classmethod
        def validate_age(cls, v):
            if v < 0:
                raise ValueError("Age must be positive")
            return v

    @app.post("/test/validation-error")
    async def validation_error_route(data: TestModel):
        return {"message": "Success"}

    return app


@pytest.fixture
def client(test_app):
    """Create a test client for the FastAPI application."""
    return TestClient(test_app, raise_server_exceptions=False)


# ============================================================================
# TEST CUSTOM EXCEPTION CLASSES
# ============================================================================


class TestCustomExceptionClasses:
    """Test custom exception class structure and initialization."""

    def test_app_exception_structure(self):
        """Test AppException base class structure."""
        exc = AppException("Test message", status_code=500, detail={"key": "value"})

        assert exc.message == "Test message"
        assert exc.status_code == 500
        assert exc.detail == {"key": "value"}
        assert str(exc) == "Test message"

    def test_app_exception_default_values(self):
        """Test AppException with default values."""
        exc = AppException("Test message")

        assert exc.message == "Test message"
        assert exc.status_code == 500
        assert exc.detail is None

    def test_not_found_exception(self):
        """Test NotFoundException raises with 404 status."""
        exc = NotFoundException("User not found")

        assert exc.message == "User not found"
        assert exc.status_code == 404
        assert exc.detail is None

    def test_not_found_exception_default_message(self):
        """Test NotFoundException with default message."""
        exc = NotFoundException()

        assert exc.message == "Resource not found"
        assert exc.status_code == 404

    def test_unauthorized_exception(self):
        """Test UnauthorizedException raises with 401 status."""
        exc = UnauthorizedException("Invalid token")

        assert exc.message == "Invalid token"
        assert exc.status_code == 401

    def test_forbidden_exception(self):
        """Test ForbiddenException raises with 403 status."""
        exc = ForbiddenException("Admin access required")

        assert exc.message == "Admin access required"
        assert exc.status_code == 403

    def test_bad_request_exception(self):
        """Test BadRequestException raises with 400 status."""
        exc = BadRequestException("Missing required field")

        assert exc.message == "Missing required field"
        assert exc.status_code == 400

    def test_conflict_exception(self):
        """Test ConflictException raises with 409 status."""
        exc = ConflictException("Email already exists")

        assert exc.message == "Email already exists"
        assert exc.status_code == 409

    def test_validation_exception(self):
        """Test ValidationException raises with 422 status."""
        exc = ValidationException("Invalid email format")

        assert exc.message == "Invalid email format"
        assert exc.status_code == 422

    def test_rate_limit_exception(self):
        """Test RateLimitException raises with 429 status."""
        exc = RateLimitException()

        assert exc.message == "Rate limit exceeded"
        assert exc.status_code == 429

    def test_external_api_exception(self):
        """Test ExternalAPIException raises with 502 status."""
        exc = ExternalAPIException("API timeout")

        assert exc.message == "API timeout"
        assert exc.status_code == 502

    def test_database_exception(self):
        """Test DatabaseException raises with 500 status."""
        exc = DatabaseException("Connection pool exhausted")

        assert exc.message == "Connection pool exhausted"
        assert exc.status_code == 500

    def test_cache_exception(self):
        """Test CacheException raises with 500 status."""
        exc = CacheException("Redis connection failed")

        assert exc.message == "Redis connection failed"
        assert exc.status_code == 500

    def test_exception_with_detail(self):
        """Test exception with detail field."""
        detail = {"field": "email", "reason": "invalid format"}
        exc = ValidationException("Validation failed", detail=detail)

        assert exc.detail == detail


# ============================================================================
# TEST ERROR RESPONSE FORMATTING
# ============================================================================


class TestErrorResponseFormat:
    """Test error response format consistency."""

    def test_app_exception_response_format(self, client):
        """Test AppException returns consistent JSON format."""
        response = client.get("/test/app-exception")

        assert response.status_code == 500
        assert "success" in response.json()
        assert "message" in response.json()
        assert "detail" in response.json()
        assert response.json()["success"] is False

    def test_error_response_includes_message(self, client):
        """Test error responses include error message."""
        response = client.get("/test/not-found")

        assert response.status_code == 404
        assert response.json()["message"] == "Resource not found"

    def test_error_response_includes_details(self, client):
        """Test error responses include detail field when provided."""
        response = client.get("/test/app-exception")

        assert response.json()["detail"] == {"key": "value"}

    def test_error_response_status_codes(self, client):
        """Test error responses return correct HTTP status codes."""
        test_cases = [
            ("/test/not-found", 404),
            ("/test/unauthorized", 401),
            ("/test/forbidden", 403),
            ("/test/bad-request", 400),
            ("/test/conflict", 409),
            ("/test/validation", 422),
            ("/test/rate-limit", 429),
            ("/test/external-api", 502),
            ("/test/database", 500),
            ("/test/cache", 500),
        ]

        for endpoint, expected_status in test_cases:
            response = client.get(endpoint)
            assert response.status_code == expected_status, f"Failed for {endpoint}"

    def test_success_field_always_false(self, client):
        """Test all error responses have success=False."""
        endpoints = [
            "/test/not-found",
            "/test/unauthorized",
            "/test/forbidden",
            "/test/validation",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.json()["success"] is False, f"Failed for {endpoint}"


# ============================================================================
# TEST EXCEPTION HANDLER INTEGRATION
# ============================================================================


class TestExceptionHandlerIntegration:
    """Test exception handlers integration with FastAPI."""

    def test_app_exception_handler_registration(self, client):
        """Test AppException handler is registered and working."""
        response = client.get("/test/app-exception")

        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
        assert data["message"] == "Test app exception"
        assert data["detail"] == {"key": "value"}

    def test_validation_error_handler(self, client):
        """Test Pydantic validation errors formatted correctly."""
        # Missing required field
        response = client.post("/test/validation-error", json={})

        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["message"] == "Validation error"
        assert "detail" in data
        assert isinstance(data["detail"], list)

    def test_validation_error_format(self, client):
        """Test validation error detail format."""
        response = client.post("/test/validation-error", json={"name": "John"})

        data = response.json()
        errors = data["detail"]
        assert len(errors) > 0

        # Check error structure
        error = errors[0]
        assert "field" in error
        assert "message" in error
        assert "type" in error

    def test_sqlalchemy_exception_handler(self, client):
        """Test SQLAlchemy errors handled correctly."""
        response = client.get("/test/sqlalchemy")

        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
        assert data["message"] == "Database error occurred"
        # Detail should be None in non-debug mode
        assert data["detail"] is None

    def test_generic_exception_handler(self, client):
        """Test unexpected exceptions return 500 with generic message."""
        response = client.get("/test/generic")

        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
        assert data["message"] == "Internal server error"
        # Detail should be None in non-debug mode
        assert data["detail"] is None

    def test_no_sensitive_information_in_production(self, client):
        """Test no stack traces or sensitive data in production responses."""
        # App is in debug=False mode
        endpoints = ["/test/database", "/test/generic", "/test/sqlalchemy"]

        for endpoint in endpoints:
            response = client.get(endpoint)
            data = response.json()

            # Detail should be None in production (debug=False)
            assert data["detail"] is None, f"Sensitive data leaked in {endpoint}"
            # Should not contain stack trace
            assert "Traceback" not in str(response.content)

    @pytest.mark.asyncio
    async def test_app_exception_handler_direct(self):
        """Test app_exception_handler function directly."""
        # Create a mock request
        app = FastAPI()
        request = Request(
            scope={"type": "http", "app": app, "method": "GET", "path": "/"}
        )

        exc = AppException("Test error", status_code=418, detail={"info": "test"})
        response = await app_exception_handler(request, exc)

        assert response.status_code == 418
        assert response.body == (
            b'{"success":false,"message":"Test error","detail":{"info":"test"}}'
        )

    @pytest.mark.asyncio
    async def test_generic_exception_handler_direct(self):
        """Test generic_exception_handler function directly."""
        app = FastAPI(debug=False)
        request = Request(
            scope={"type": "http", "app": app, "method": "GET", "path": "/"}
        )

        exc = ValueError("Unexpected error")
        response = await generic_exception_handler(request, exc)

        assert response.status_code == 500
        data = response.body.decode()
        assert "Internal server error" in data
        # Detail should be None in non-debug mode
        assert '"detail":null' in data


# ============================================================================
# TEST EXCEPTION CHAINING
# ============================================================================


class TestExceptionChaining:
    """Test exception chaining and original exception preservation."""

    def test_exception_inheritance(self):
        """Test all custom exceptions inherit from AppException."""
        exceptions = [
            NotFoundException,
            UnauthorizedException,
            ForbiddenException,
            BadRequestException,
            ConflictException,
            ValidationException,
            RateLimitException,
            ExternalAPIException,
            DatabaseException,
            CacheException,
        ]

        for exc_class in exceptions:
            exc = exc_class("Test")
            assert isinstance(exc, AppException)
            assert isinstance(exc, Exception)

    def test_exception_message_preserved(self):
        """Test exception messages are preserved through inheritance."""
        exc = NotFoundException("Specific resource not found")

        assert str(exc) == "Specific resource not found"
        assert exc.message == "Specific resource not found"


# ============================================================================
# TEST EDGE CASES
# ============================================================================


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_exception_with_empty_message(self):
        """Test exception with empty message."""
        exc = AppException("", status_code=500)

        assert exc.message == ""
        assert exc.status_code == 500

    def test_exception_with_none_detail(self):
        """Test exception with None detail."""
        exc = AppException("Test", detail=None)

        assert exc.detail is None

    def test_exception_with_complex_detail(self):
        """Test exception with complex nested detail."""
        detail = {
            "errors": [
                {"field": "email", "message": "Invalid format"},
                {"field": "age", "message": "Must be positive"},
            ],
            "metadata": {"timestamp": "2024-01-01", "request_id": "abc123"},
        }
        exc = ValidationException("Multiple validation errors", detail=detail)

        assert exc.detail == detail

    def test_multiple_validation_errors(self, client):
        """Test validation error with multiple fields."""
        # Invalid data: wrong type for age
        response = client.post(
            "/test/validation-error", json={"name": "John", "age": "invalid"}
        )

        assert response.status_code == 422
        data = response.json()
        assert len(data["detail"]) > 0

    def test_exception_user_friendly_messages(self):
        """Test exception messages are user-friendly."""
        exceptions = [
            (NotFoundException(), "Resource not found"),
            (UnauthorizedException(), "Unauthorized"),
            (ForbiddenException(), "Forbidden"),
            (BadRequestException(), "Bad request"),
            (ValidationException(), "Validation error"),
        ]

        for exc, expected_message in exceptions:
            assert exc.message == expected_message
