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


class EmailVerificationRequest(BaseModel):
    """Schema for email verification"""

    token: str = Field(..., min_length=1, description="Email verification token")


class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""

    email: EmailStr = Field(..., description="Email address for password reset")


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""

    token: str = Field(..., min_length=1, description="Password reset token")
    new_password: str = Field(
        ..., min_length=8, max_length=100, description="New password"
    )

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets minimum strength requirements"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        # Check for uppercase
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")

        # Check for lowercase
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")

        # Check for digit
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")

        # Check for special character
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(char in special_chars for char in v):
            raise ValueError("Password must contain at least one special character")

        return v


class VerificationStatusResponse(BaseModel):
    """Schema for email verification status"""

    email_verified: bool
    email_verified_at: Optional[datetime] = None
    pending_tokens_count: int
    can_resend: bool


class SuccessResponse(BaseModel):
    """Generic success response"""

    success: bool
    message: str
