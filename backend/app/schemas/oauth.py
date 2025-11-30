"""OAuth Pydantic schemas for social login"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class OAuthProviderEnum(str, Enum):
    """Supported OAuth providers"""

    GOOGLE = "google"
    KAKAO = "kakao"
    NAVER = "naver"


class OAuthAuthorizationResponse(BaseModel):
    """Response containing OAuth authorization URL"""

    authorization_url: str = Field(
        ..., description="URL to redirect user for OAuth authorization"
    )
    state: str = Field(..., description="State token for CSRF protection")
    provider: OAuthProviderEnum = Field(..., description="OAuth provider")


class OAuthCallbackRequest(BaseModel):
    """Request for OAuth callback handling"""

    code: str = Field(..., description="Authorization code from OAuth provider")
    state: str = Field(..., description="State token for CSRF validation")


class OAuthUserInfo(BaseModel):
    """User information from OAuth provider"""

    provider: OAuthProviderEnum
    provider_user_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None


class SocialAccountResponse(BaseModel):
    """Response for a linked social account"""

    id: int
    provider: str
    provider_email: Optional[str] = None
    provider_name: Optional[str] = None
    provider_picture: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SocialAccountsListResponse(BaseModel):
    """Response containing list of linked social accounts"""

    accounts: List[SocialAccountResponse]
    total: int


class OAuthLinkRequest(BaseModel):
    """Request to link a social account"""

    code: str = Field(..., description="Authorization code from OAuth provider")
    state: str = Field(..., description="State token for CSRF validation")


class OAuthUnlinkResponse(BaseModel):
    """Response for unlinking a social account"""

    success: bool
    message: str
    provider: str


class OAuthTokenResponse(BaseModel):
    """OAuth token response from provider"""

    access_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None


class OAuthErrorResponse(BaseModel):
    """OAuth error response"""

    error: str
    error_description: Optional[str] = None
    provider: Optional[str] = None
