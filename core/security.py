"""
Security utilities - JWT, API keys, password hashing.
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple

import jwt
from passlib.context import CryptContext

from .config import settings
from .exceptions import AuthenticationError


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password for storage."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


# JWT Token handling

def create_access_token(
    user_id: str,
    email: Optional[str] = None,
    scopes: Optional[list] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT access token."""
    if expires_delta is None:
        expires_delta = timedelta(hours=settings.jwt_expiration_hours)

    expire = datetime.utcnow() + expires_delta

    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
    }

    if email:
        payload["email"] = email
    if scopes:
        payload["scopes"] = scopes

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        if payload.get("type") != "access":
            raise AuthenticationError("Invalid token type")

        return payload

    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise AuthenticationError(f"Invalid token: {str(e)}")


def create_refresh_token(user_id: str) -> str:
    """Create a refresh token."""
    expire = datetime.utcnow() + timedelta(days=30)

    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_refresh_token(token: str) -> dict:
    """Decode and validate a refresh token."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        if payload.get("type") != "refresh":
            raise AuthenticationError("Invalid token type")

        return payload

    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Refresh token has expired")
    except jwt.InvalidTokenError as e:
        raise AuthenticationError(f"Invalid refresh token: {str(e)}")


# API Key handling

def generate_api_key() -> Tuple[str, str]:
    """
    Generate a new API key.
    Returns (api_key, key_hash) - api_key is shown to user once, key_hash is stored.
    """
    # Generate a secure random key
    api_key = f"cca_{secrets.token_urlsafe(32)}"  # cca = career coach api

    # Hash the key for storage
    key_hash = hash_api_key(api_key)

    return api_key, key_hash


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(api_key: str, stored_hash: str) -> bool:
    """Verify an API key against its stored hash."""
    return hash_api_key(api_key) == stored_hash


# Utility functions

def generate_request_id() -> str:
    """Generate a unique request ID."""
    return secrets.token_hex(4)


def generate_user_id() -> str:
    """Generate a unique user ID."""
    return f"usr_{secrets.token_urlsafe(16)}"


def generate_conversation_id() -> str:
    """Generate a unique conversation ID."""
    return f"conv_{secrets.token_urlsafe(12)}"
