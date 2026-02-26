"""Base OAuth provider abstract class"""

from abc import ABC, abstractmethod
from typing import Optional
from urllib.parse import urlencode

import httpx

from app.schemas.oauth import OAuthTokenResponse, OAuthUserInfo


class BaseOAuthProvider(ABC):
    """
    Abstract base class for OAuth providers.

    All OAuth providers must implement:
    - get_authorization_url(): Generate the OAuth authorization URL
    - exchange_code_for_token(): Exchange authorization code for access token
    - get_user_info(): Fetch user information using access token
    """

    # Override these in subclasses
    AUTHORIZATION_URL: str = ""
    TOKEN_URL: str = ""
    USERINFO_URL: str = ""
    SCOPES: list[str] = []
    PROVIDER_NAME: str = ""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
    ):
        """
        Initialize OAuth provider.

        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            redirect_uri: Redirect URI after OAuth authorization
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self._http_client: Optional[httpx.AsyncClient] = None

    @property
    def http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client

    async def close(self) -> None:
        """Close HTTP client"""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()

    def get_authorization_url(self, state: str) -> str:
        """
        Generate OAuth authorization URL.

        Args:
            state: State token for CSRF protection

        Returns:
            Authorization URL to redirect user to
        """
        params = self._build_authorization_params(state)
        return f"{self.AUTHORIZATION_URL}?{urlencode(params)}"

    def _build_authorization_params(self, state: str) -> dict:
        """
        Build authorization URL parameters.
        Override in subclasses for provider-specific params.

        Args:
            state: State token for CSRF protection

        Returns:
            Dictionary of URL parameters
        """
        return {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "state": state,
            "scope": " ".join(self.SCOPES),
        }

    @abstractmethod
    async def exchange_code_for_token(self, code: str) -> OAuthTokenResponse:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from OAuth provider

        Returns:
            OAuthTokenResponse with access token and optional refresh token

        Raises:
            httpx.HTTPStatusError: If token exchange fails
        """
        pass

    @abstractmethod
    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """
        Fetch user information using access token.

        Args:
            access_token: OAuth access token

        Returns:
            OAuthUserInfo with user's profile data

        Raises:
            httpx.HTTPStatusError: If user info request fails
        """
        pass

    async def _post_token_request(
        self, code: str, extra_params: Optional[dict] = None
    ) -> dict:
        """
        Make POST request to token endpoint.

        Args:
            code: Authorization code
            extra_params: Additional provider-specific parameters

        Returns:
            Token response as dictionary
        """
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }

        if extra_params:
            data.update(extra_params)

        response = await self.http_client.post(
            self.TOKEN_URL,
            data=data,
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        return response.json()

    async def _get_userinfo_request(
        self, access_token: str, headers: Optional[dict] = None
    ) -> dict:
        """
        Make GET request to userinfo endpoint.

        Args:
            access_token: OAuth access token
            headers: Additional headers

        Returns:
            User info response as dictionary
        """
        default_headers = {"Authorization": f"Bearer {access_token}"}
        if headers:
            default_headers.update(headers)

        response = await self.http_client.get(
            self.USERINFO_URL,
            headers=default_headers,
        )
        response.raise_for_status()
        return response.json()
