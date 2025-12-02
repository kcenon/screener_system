"""Google OAuth provider implementation"""

from app.schemas.oauth import (OAuthProviderEnum, OAuthTokenResponse,
                               OAuthUserInfo)

from .base import BaseOAuthProvider


class GoogleOAuthProvider(BaseOAuthProvider):
    """
    Google OAuth 2.0 provider.

    Implements OAuth flow for Google accounts using OpenID Connect.
    Scopes: openid, email, profile
    """

    AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    SCOPES = ["openid", "email", "profile"]
    PROVIDER_NAME = "GOOGLE"

    def _build_authorization_params(self, state: str) -> dict:
        """Build Google-specific authorization parameters"""
        params = super()._build_authorization_params(state)
        # Google-specific parameters
        params["access_type"] = "offline"  # Request refresh token
        params["prompt"] = "consent"  # Force consent screen for refresh token
        return params

    async def exchange_code_for_token(self, code: str) -> OAuthTokenResponse:
        """
        Exchange authorization code for Google access token.

        Args:
            code: Authorization code from Google

        Returns:
            OAuthTokenResponse with access token and refresh token
        """
        token_data = await self._post_token_request(code)

        return OAuthTokenResponse(
            access_token=token_data["access_token"],
            token_type=token_data.get("token_type", "Bearer"),
            expires_in=token_data.get("expires_in"),
            refresh_token=token_data.get("refresh_token"),
            scope=token_data.get("scope"),
        )

    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """
        Fetch user information from Google.

        Args:
            access_token: Google access token

        Returns:
            OAuthUserInfo with Google profile data
        """
        user_data = await self._get_userinfo_request(access_token)

        return OAuthUserInfo(
            provider=OAuthProviderEnum.GOOGLE,
            provider_user_id=user_data["id"],
            email=user_data.get("email"),
            name=user_data.get("name"),
            picture=user_data.get("picture"),
        )
