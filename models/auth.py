"""
Authentication models.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, EmailStr


class TokenRequest(BaseModel):
    """Request for JWT token."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    user_id: str = Field(..., description="User ID")


class RefreshTokenRequest(BaseModel):
    """Request to refresh token."""

    refresh_token: str = Field(..., description="Refresh token")


class APIKeyCreate(BaseModel):
    """Request to create API key."""

    name: str = Field(..., min_length=1, max_length=100, description="API key name")
    scopes: List[str] = Field(
        default=["read"],
        description="API key scopes (read, write, admin)"
    )
    expires_days: Optional[int] = Field(
        default=365,
        ge=1,
        le=3650,
        description="Days until expiration"
    )


class APIKeyResponse(BaseModel):
    """API key response."""

    key_id: str = Field(..., description="API key ID")
    api_key: str = Field(..., description="API key (only shown once)")
    name: str = Field(..., description="API key name")
    scopes: List[str] = Field(..., description="API key scopes")
    created_at: datetime = Field(..., description="Creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")


class APIKeyInfo(BaseModel):
    """API key info (without the actual key)."""

    key_id: str
    name: str
    scopes: List[str]
    created_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    is_active: bool


class CurrentUser(BaseModel):
    """Current authenticated user."""

    user_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    scopes: List[str] = Field(default_factory=list)
    auth_method: str = Field(default="jwt", description="jwt or api_key")
