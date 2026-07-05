"""
Authentication dependencies for FastAPI.
"""

from typing import List, Optional

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.config import settings
from core.exceptions import AuthenticationError, AuthorizationError
from core.security import decode_access_token, verify_api_key
from models.auth import CurrentUser

# Security schemes
bearer_scheme = HTTPBearer(auto_error=False)


async def get_token_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Optional[CurrentUser]:
    """
    Extract user from JWT bearer token.
    Returns None if no token provided (for optional auth).
    """
    if credentials is None:
        return None

    try:
        payload = decode_access_token(credentials.credentials)
        return CurrentUser(
            user_id=payload["sub"],
            email=payload.get("email"),
            scopes=payload.get("scopes", []),
            auth_method="jwt",
        )
    except AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_api_key_user(
    api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> Optional[CurrentUser]:
    """
    Extract user from API key header.
    Returns None if no API key provided.

    In production, this would look up the API key in a database.
    For simplicity, we're using a basic validation.
    """
    if api_key is None:
        return None

    # In production: look up API key in database
    # For now, validate format and return a basic user
    if not api_key.startswith("cca_"):
        return None

    # TODO: Look up API key in database and get user/scopes
    # For now, return a basic authenticated user
    return CurrentUser(
        user_id="api_user",
        scopes=["read", "write"],
        auth_method="api_key",
    )


async def get_current_user(
    token_user: Optional[CurrentUser] = Depends(get_token_user),
    api_key_user: Optional[CurrentUser] = Depends(get_api_key_user),
) -> CurrentUser:
    """
    Get current authenticated user from either JWT or API key.
    Raises 401 if no valid authentication provided.
    """
    user = token_user or api_key_user

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_user_optional(
    token_user: Optional[CurrentUser] = Depends(get_token_user),
    api_key_user: Optional[CurrentUser] = Depends(get_api_key_user),
) -> Optional[CurrentUser]:
    """
    Get current user if authenticated, None otherwise.
    Use this for endpoints that work with or without auth.
    """
    return token_user or api_key_user


def require_scopes(required_scopes: List[str]):
    """
    Dependency factory to check user has required scopes.

    Usage:
        @app.get("/admin", dependencies=[Depends(require_scopes(["admin"]))])
        async def admin_endpoint():
            ...
    """
    async def scope_checker(
        user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        for scope in required_scopes:
            if scope not in user.scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Required scope '{scope}' not found",
                )
        return user

    return scope_checker


class AuthRequired:
    """
    Class-based dependency for auth with scope checking.

    Usage:
        @app.get("/endpoint")
        async def endpoint(user: CurrentUser = Depends(AuthRequired(scopes=["write"]))):
            ...
    """

    def __init__(self, scopes: Optional[List[str]] = None):
        self.required_scopes = scopes or []

    async def __call__(
        self,
        token_user: Optional[CurrentUser] = Depends(get_token_user),
        api_key_user: Optional[CurrentUser] = Depends(get_api_key_user),
    ) -> CurrentUser:
        user = token_user or api_key_user

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        for scope in self.required_scopes:
            if scope not in user.scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Required scope '{scope}' not found",
                )

        return user
