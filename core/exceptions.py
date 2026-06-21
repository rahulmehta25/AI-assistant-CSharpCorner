"""
Custom exception classes for the application.
Provides structured error handling with consistent error responses.
"""

from typing import Any, Dict, Optional


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": True,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class AuthenticationError(AppException):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details,
        )


class AuthorizationError(AppException):
    """Raised when authorization fails."""

    def __init__(
        self,
        message: str = "Access denied",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
            details=details,
        )


class NotFoundError(AppException):
    """Raised when a resource is not found."""

    def __init__(
        self,
        resource: str,
        identifier: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with ID '{identifier}' not found"

        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=404,
            details=details,
        )


class ValidationError(AppException):
    """Raised when request validation fails."""

    def __init__(
        self,
        message: str = "Validation error",
        errors: Optional[list] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        if errors:
            details["validation_errors"] = errors

        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=422,
            details=details,
        )


class RateLimitError(AppException):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        if retry_after:
            details["retry_after_seconds"] = retry_after

        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details=details,
        )


class AIServiceError(AppException):
    """Raised when AI service (OpenAI/LangChain) fails."""

    def __init__(
        self,
        message: str = "AI service error",
        service: str = "openai",
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details["service"] = service

        super().__init__(
            message=message,
            error_code="AI_SERVICE_ERROR",
            status_code=503,
            details=details,
        )


class CacheError(AppException):
    """Raised when caching operations fail."""

    def __init__(
        self,
        message: str = "Cache operation failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code="CACHE_ERROR",
            status_code=500,
            details=details,
        )


class ExternalServiceError(AppException):
    """Raised when external service calls fail."""

    def __init__(
        self,
        service: str,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details["service"] = service

        super().__init__(
            message=message or f"External service '{service}' unavailable",
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=502,
            details=details,
        )
