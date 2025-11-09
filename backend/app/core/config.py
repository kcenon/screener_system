"""Application configuration settings"""

from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, validator
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

    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list"""
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    # ========================================================================
    # RATE LIMITING
    # ========================================================================

    RATE_LIMIT_FREE: int = 100
    RATE_LIMIT_BASIC: int = 500
    RATE_LIMIT_PRO: int = 2000

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
