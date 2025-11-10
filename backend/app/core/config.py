"""Application configuration settings"""

from functools import lru_cache
from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # ========================================================================
    # GENERAL
    # ========================================================================

    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    PROJECT_NAME: str = "Stock Screening Platform"
    VERSION: str = "0.1.0"

    # ========================================================================
    # DATABASE
    # ========================================================================

    DATABASE_URL: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False

    # ========================================================================
    # REDIS
    # ========================================================================

    REDIS_URL: str
    CACHE_TTL_HOT_STOCKS: int = 300
    CACHE_TTL_STOCK_DETAIL: int = 3600
    CACHE_TTL_SCREENING: int = 600

    # ========================================================================
    # AUTHENTICATION & SECURITY
    # ========================================================================

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ========================================================================
    # CORS
    # ========================================================================

    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v) -> List[str]:
        """Parse CORS origins from comma-separated string or list"""
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return []  # Default to empty list if neither string nor list

    # ========================================================================
    # RATE LIMITING
    # ========================================================================

    # General API rate limits (requests per hour)
    RATE_LIMIT_FREE: int = 100  # 100 req/hour
    RATE_LIMIT_BASIC: int = 1000  # 1000 req/hour
    RATE_LIMIT_PRO: int = 10000  # 10000 req/hour
    RATE_LIMIT_WINDOW: int = 3600  # Rate limit window in seconds (1 hour)

    # Per-endpoint rate limits (requests per hour)
    # These limits are in addition to general tier limits
    RATE_LIMIT_SCREENING: int = 50  # Screening queries (more expensive)
    RATE_LIMIT_STOCK_DETAIL: int = 200  # Stock detail queries
    RATE_LIMIT_AUTH: int = 10  # Authentication endpoints (prevent brute force)

    RATE_LIMIT_WHITELIST_PATHS: Union[str, List[str]] = [
        "/health",
        "/health/db",
        "/health/redis",
        "/docs",
        "/redoc",
        "/openapi.json",
    ]

    @field_validator("RATE_LIMIT_WHITELIST_PATHS", mode="before")
    @classmethod
    def parse_whitelist_paths(cls, v) -> List[str]:
        """Parse whitelist paths from comma-separated string or list"""
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return []

    # ========================================================================
    # EXTERNAL API QUOTA (KIS API)
    # ========================================================================

    KIS_API_RATE_LIMIT: int = 20  # 20 requests per second
    KIS_API_QUOTA_WINDOW: int = 1  # 1 second window
    KIS_API_ENABLE_QUEUE: bool = True  # Enable request queuing
    KIS_API_QUEUE_TIMEOUT: int = 30  # Queue timeout in seconds
    KIS_API_CIRCUIT_BREAKER_THRESHOLD: int = 5  # Failures before opening circuit
    KIS_API_CIRCUIT_BREAKER_TIMEOUT: int = 60  # Circuit breaker timeout in seconds

    # ========================================================================
    # EXTERNAL APIs
    # ========================================================================

    KRX_API_KEY: str = ""
    KRX_API_URL: str = "https://api.krx.co.kr"

    FGUIDE_API_KEY: str = ""
    FGUIDE_API_URL: str = "https://api.fguide.com"

    # ========================================================================
    # CELERY
    # ========================================================================

    CELERY_BROKER_URL: str = ""
    CELERY_RESULT_BACKEND: str = ""

    # ========================================================================
    # MONITORING
    # ========================================================================

    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "development"

    class Config:
        """Pydantic configuration"""

        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
