"""
Core module - Configuration, auth, middleware, and shared utilities.
"""

from .config import settings
from .exceptions import (
    AppException,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    AIServiceError,
)
from .logging import setup_logging, get_logger

__all__ = [
    "settings",
    "AppException",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "AIServiceError",
    "setup_logging",
    "get_logger",
]
