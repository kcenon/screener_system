"""Kakao OAuth provider implementation"""

from app.schemas.oauth import (OAuthProviderEnum, OAuthTokenResponse,
                               OAuthUserInfo)

from .base import BaseOAuthProvider


class KakaoOAuthProvider(BaseOAuthProvider):
    """
    Kakao OAuth 2.0 provider.

    Implements OAuth flow for Kakao accounts (popular in South Korea).
    Requires Kakao Developers app registration.
    """

    AUTHORIZATION_URL = "https://kauth.kakao.com/oauth/authorize"
    TOKEN_URL = "https://kauth.kakao.com/oauth/token"
    USERINFO_URL = "https://kapi.kakao.com/v2/user/me"
    # Kakao uses different scope format
    SCOPES = ["profile_nickname", "profile_image", "account_email"]
    PROVIDER_NAME = "KAKAO"

    def _build_authorization_params(self, state: str) -> dict:
        """Build Kakao-specific authorization parameters"""
        return {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "state": state,
            # Kakao uses comma-separated scopes
            "scope": ",".join(self.SCOPES),
        }

    async def exchange_code_for_token(self, code: str) -> OAuthTokenResponse:
        """
        Exchange authorization code for Kakao access token.

        Args:
            code: Authorization code from Kakao

        Returns:
            OAuthTokenResponse with access token and refresh token
        """
        # Kakao requires content-type: application/x-www-form-urlencoded
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": code,
        }

        response = await self.http_client.post(
            self.TOKEN_URL,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        token_data = response.json()

        return OAuthTokenResponse(
            access_token=token_data["access_token"],
            token_type=token_data.get("token_type", "Bearer"),
            expires_in=token_data.get("expires_in"),
            refresh_token=token_data.get("refresh_token"),
            scope=token_data.get("scope"),
        )

    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """
        Fetch user information from Kakao.

        Args:
            access_token: Kakao access token

        Returns:
            OAuthUserInfo with Kakao profile data
        """
        user_data = await self._get_userinfo_request(access_token)

        # Kakao has nested response structure
        kakao_account = user_data.get("kakao_account", {})
        profile = kakao_account.get("profile", {})

        return OAuthUserInfo(
            provider=OAuthProviderEnum.KAKAO,
            provider_user_id=str(user_data["id"]),
            email=kakao_account.get("email"),
            name=profile.get("nickname"),
            picture=profile.get("profile_image_url"),
        )
