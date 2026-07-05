"""
Authentication endpoints.
"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status

from core.config import settings
from core.security import (
    create_access_token,
    create_refresh_token,
    generate_api_key,
    generate_user_id,
    hash_password,
    verify_password,
)
from models.auth import (
    APIKeyCreate,
    APIKeyResponse,
    CurrentUser,
    RefreshTokenRequest,
    TokenRequest,
    TokenResponse,
)
from api.dependencies.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/token", response_model=TokenResponse)
async def login(request: TokenRequest):
    """
    Authenticate and get JWT token.

    In production, this would verify against a user database.
    """
    # TODO: In production, verify against actual user database
    # For demo, accept any valid email format with password >= 8 chars
    if len(request.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Generate user ID (in production, this would come from database)
    user_id = generate_user_id()

    # Create token
    access_token = create_access_token(
        user_id=user_id,
        email=request.email,
        scopes=["read", "write"],
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.jwt_expiration_hours * 3600,
        user_id=user_id,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh an access token using a refresh token.
    """
    from core.security import decode_refresh_token
    from core.exceptions import AuthenticationError

    try:
        payload = decode_refresh_token(request.refresh_token)
        user_id = payload["sub"]

        # Create new access token
        access_token = create_access_token(
            user_id=user_id,
            scopes=["read", "write"],
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.jwt_expiration_hours * 3600,
            user_id=user_id,
        )

    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    request: APIKeyCreate,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Create a new API key.

    The API key is only shown once - store it securely.
    """
    api_key, key_hash = generate_api_key()

    # TODO: Store key_hash in database associated with user

    return APIKeyResponse(
        key_id=f"key_{current_user.user_id[:8]}",
        api_key=api_key,
        name=request.name,
        scopes=request.scopes,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=request.expires_days or 365),
    )


@router.get("/me", response_model=CurrentUser)
async def get_current_user_info(
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Get current authenticated user information.
    """
    return current_user
