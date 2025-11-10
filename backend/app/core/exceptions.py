"""Custom exception classes"""

from typing import Any, Optional


class AppException(Exception):
    """Base exception class for application errors"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        detail: Optional[Any] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class NotFoundException(AppException):
    """Exception raised when resource is not found"""

    def __init__(
        self, message: str = "Resource not found", detail: Optional[Any] = None
    ):
        super().__init__(message, status_code=404, detail=detail)


class UnauthorizedException(AppException):
    """Exception raised when authentication fails"""

    def __init__(self, message: str = "Unauthorized", detail: Optional[Any] = None):
        super().__init__(message, status_code=401, detail=detail)


class ForbiddenException(AppException):
    """Exception raised when user lacks permissions"""

    def __init__(self, message: str = "Forbidden", detail: Optional[Any] = None):
        super().__init__(message, status_code=403, detail=detail)


class BadRequestException(AppException):
    """Exception raised when request is invalid"""

    def __init__(self, message: str = "Bad request", detail: Optional[Any] = None):
        super().__init__(message, status_code=400, detail=detail)


class ConflictException(AppException):
    """Exception raised when resource conflict occurs"""

    def __init__(self, message: str = "Conflict", detail: Optional[Any] = None):
        super().__init__(message, status_code=409, detail=detail)


class ValidationException(AppException):
    """Exception raised when validation fails"""

    def __init__(self, message: str = "Validation error", detail: Optional[Any] = None):
        super().__init__(message, status_code=422, detail=detail)


class RateLimitException(AppException):
    """Exception raised when rate limit is exceeded"""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        detail: Optional[Any] = None,
    ):
        super().__init__(message, status_code=429, detail=detail)


class ExternalAPIException(AppException):
    """Exception raised when external API call fails"""

    def __init__(
        self,
        message: str = "External API error",
        detail: Optional[Any] = None,
    ):
        super().__init__(message, status_code=502, detail=detail)


class DatabaseException(AppException):
    """Exception raised when database operation fails"""

    def __init__(
        self,
        message: str = "Database error",
        detail: Optional[Any] = None,
    ):
        super().__init__(message, status_code=500, detail=detail)


class CacheException(AppException):
    """Exception raised when cache operation fails"""

    def __init__(
        self,
        message: str = "Cache error",
        detail: Optional[Any] = None,
    ):
        super().__init__(message, status_code=500, detail=detail)
