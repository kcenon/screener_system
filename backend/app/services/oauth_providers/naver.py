"""Naver OAuth provider implementation"""

from app.schemas.oauth import (OAuthProviderEnum, OAuthTokenResponse,
                               OAuthUserInfo)

from .base import BaseOAuthProvider


class NaverOAuthProvider(BaseOAuthProvider):
    """
    Naver OAuth 2.0 provider.

    Implements OAuth flow for Naver accounts (popular in South Korea).
    Requires Naver Developers app registration.
    """

    AUTHORIZATION_URL = "https://nid.naver.com/oauth2.0/authorize"
    TOKEN_URL = "https://nid.naver.com/oauth2.0/token"
    USERINFO_URL = "https://openapi.naver.com/v1/nid/me"
    # Naver doesn't use scopes in the same way; permissions are set in developer console
    SCOPES = []
    PROVIDER_NAME = "NAVER"

    def _build_authorization_params(self, state: str) -> dict:
        """Build Naver-specific authorization parameters"""
        return {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "state": state,
        }

    async def exchange_code_for_token(self, code: str) -> OAuthTokenResponse:
        """
        Exchange authorization code for Naver access token.

        Args:
            code: Authorization code from Naver

        Returns:
            OAuthTokenResponse with access token and refresh token
        """
        # Naver uses query parameters for token request
        params = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "state": "state",  # Naver requires state in token request
        }

        response = await self.http_client.post(
            self.TOKEN_URL,
            params=params,
        )
        response.raise_for_status()
        token_data = response.json()

        # Naver returns error in response body, not HTTP status
        if "error" in token_data:
            raise ValueError(
                f"Naver OAuth error: "
                f"{token_data.get('error_description', token_data['error'])}"
            )

        return OAuthTokenResponse(
            access_token=token_data["access_token"],
            token_type=token_data.get("token_type", "Bearer"),
            expires_in=int(token_data.get("expires_in", 3600)),
            refresh_token=token_data.get("refresh_token"),
        )

    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """
        Fetch user information from Naver.

        Args:
            access_token: Naver access token

        Returns:
            OAuthUserInfo with Naver profile data
        """
        user_data = await self._get_userinfo_request(access_token)

        # Naver returns error in response body
        if user_data.get("resultcode") != "00":
            raise ValueError(
                f"Naver API error: {user_data.get('message', 'Unknown error')}"
            )

        # Naver has nested response structure
        response = user_data.get("response", {})

        email = response.get("email")
        return OAuthUserInfo(
            provider=OAuthProviderEnum.NAVER,
            provider_user_id=response["id"],
            email=email,
            name=(
                response.get("name")
                or response.get("nickname")
                or (email.split("@")[0] if email else None)
            ),
            picture=response.get("profile_image"),
        )
