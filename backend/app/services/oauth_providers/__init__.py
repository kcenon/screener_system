"""OAuth providers package with factory function"""

from typing import Optional

from app.core.config import settings

from .base import BaseOAuthProvider
from .google import GoogleOAuthProvider
from .kakao import KakaoOAuthProvider
from .naver import NaverOAuthProvider

__all__ = [
    "BaseOAuthProvider",
    "GoogleOAuthProvider",
    "KakaoOAuthProvider",
    "NaverOAuthProvider",
    "get_oauth_provider",
]


def get_oauth_provider(provider_name: str) -> Optional[BaseOAuthProvider]:
    """
    Factory function to get OAuth provider instance.

    Args:
        provider_name: Name of the OAuth provider (google, kakao, naver)

    Returns:
        OAuth provider instance or None if provider is not configured

    Raises:
        ValueError: If provider is not supported
    """
    provider_name = provider_name.lower()

    if provider_name == "google":
        if not settings.GOOGLE_CLIENT_ID:
            return None
        return GoogleOAuthProvider(
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            redirect_uri=settings.GOOGLE_REDIRECT_URI,
        )

    elif provider_name == "kakao":
        if not settings.KAKAO_CLIENT_ID:
            return None
        return KakaoOAuthProvider(
            client_id=settings.KAKAO_CLIENT_ID,
            client_secret=settings.KAKAO_CLIENT_SECRET,
            redirect_uri=settings.KAKAO_REDIRECT_URI,
        )

    elif provider_name == "naver":
        if not settings.NAVER_CLIENT_ID:
            return None
        return NaverOAuthProvider(
            client_id=settings.NAVER_CLIENT_ID,
            client_secret=settings.NAVER_CLIENT_SECRET,
            redirect_uri=settings.NAVER_REDIRECT_URI,
        )

    else:
        raise ValueError(f"Unsupported OAuth provider: {provider_name}")


def is_provider_configured(provider_name: str) -> bool:
    """
    Check if OAuth provider is configured.

    Args:
        provider_name: Name of the OAuth provider

    Returns:
        True if provider credentials are configured
    """
    provider_name = provider_name.lower()

    if provider_name == "google":
        return bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)
    elif provider_name == "kakao":
        return bool(settings.KAKAO_CLIENT_ID and settings.KAKAO_CLIENT_SECRET)
    elif provider_name == "naver":
        return bool(settings.NAVER_CLIENT_ID and settings.NAVER_CLIENT_SECRET)

    return False
