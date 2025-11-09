"""User Pydantic schemas"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Base user schema with common fields"""

    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user registration"""

    password: str = Field(..., min_length=8, max_length=100)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets minimum strength requirements"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        # Check for at least one digit
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")

        # Check for at least one letter
        if not any(char.isalpha() for char in v):
            raise ValueError("Password must contain at least one letter")

        return v


class UserLogin(BaseModel):
    """Schema for user login"""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response (public data)"""

    id: int
    email: EmailStr
    name: Optional[str] = None
    subscription_tier: str
    email_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """Schema for user profile update"""

    name: Optional[str] = None
    email: Optional[EmailStr] = None

    model_config = {"from_attributes": True}


class TokenPayload(BaseModel):
    """Schema for JWT token payload"""

    sub: int  # User ID
    exp: datetime
    iat: datetime
    type: str  # "access" or "refresh"


class TokenResponse(BaseModel):
    """Schema for authentication token response"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""

    refresh_token: str
