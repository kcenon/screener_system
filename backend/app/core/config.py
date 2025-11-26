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
    # OAUTH
    # ========================================================================

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = ""

    # Kakao OAuth
    KAKAO_CLIENT_ID: str = ""
    KAKAO_CLIENT_SECRET: str = ""
    KAKAO_REDIRECT_URI: str = ""

    # Naver OAuth
    NAVER_CLIENT_ID: str = ""
    NAVER_CLIENT_SECRET: str = ""
    NAVER_REDIRECT_URI: str = ""

    # OAuth security
    OAUTH_STATE_EXPIRY_MINUTES: int = 10
    OAUTH_FRONTEND_CALLBACK_URL: str = "http://localhost:5173/auth/callback"

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
    # WEBSOCKET
    # ========================================================================

    # WebSocket limits (DoS protection)
    WEBSOCKET_MAX_MESSAGE_SIZE: int = 65536  # 64KB max message size
    WEBSOCKET_MAX_SUBSCRIPTIONS_PER_CONNECTION: int = 100  # Max subscriptions per connection
    WEBSOCKET_MAX_TARGETS_PER_SUBSCRIPTION: int = 50  # Max targets per subscribe request

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

    # ========================================================================
    # STRIPE (Payment Processing)
    # ========================================================================

    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # Stripe Price IDs (configured in Stripe Dashboard)
    STRIPE_PRICE_PREMIUM_MONTHLY: str = ""
    STRIPE_PRICE_PREMIUM_YEARLY: str = ""
    STRIPE_PRICE_PRO_MONTHLY: str = ""
    STRIPE_PRICE_PRO_YEARLY: str = ""

    # ========================================================================
    # SUBSCRIPTION SETTINGS
    # ========================================================================

    # Free tier limits
    FREE_TIER_SCREENING_LIMIT: int = 20  # Results per query
    FREE_TIER_SEARCHES_PER_DAY: int = 10

    # Trial settings
    TRIAL_PERIOD_DAYS: int = 14

    # Pricing (for display, actual prices from Stripe)
    PREMIUM_PRICE_MONTHLY: float = 9.99
    PREMIUM_PRICE_YEARLY: float = 99.00
    PRO_PRICE_MONTHLY: float = 29.99
    PRO_PRICE_YEARLY: float = 299.00

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
