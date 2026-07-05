"""
Rate limiting dependencies for FastAPI.
"""

from typing import Optional

from fastapi import Depends, Request, Response

from core.rate_limit import rate_limiter
from models.auth import CurrentUser

from .auth import get_current_user_optional


def _get_identifier(request: Request, user: Optional[CurrentUser]) -> str:
    """Get identifier for rate limiting (user_id or IP)."""
    if user:
        return f"user:{user.user_id}"

    # Fallback to IP address
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ip = forwarded.split(",")[0].strip()
    else:
        ip = request.client.host if request.client else "unknown"

    return f"ip:{ip}"


async def rate_limit_dependency(
    request: Request,
    response: Response,
    user: Optional[CurrentUser] = Depends(get_current_user_optional),
):
    """
    Rate limit dependency for standard endpoints.
    Adds rate limit headers to response.
    """
    identifier = _get_identifier(request, user)
    remaining, reset_in = rate_limiter.check_or_raise(
        identifier,
        endpoint_type="default",
    )

    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.get_usage(identifier)["limit"])
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(reset_in)


async def rate_limit_ai(
    request: Request,
    response: Response,
    user: Optional[CurrentUser] = Depends(get_current_user_optional),
):
    """
    Rate limit dependency for AI endpoints (stricter limits).
    """
    identifier = _get_identifier(request, user)
    remaining, reset_in = rate_limiter.check_or_raise(
        identifier,
        endpoint_type="ai",
    )

    # Add rate limit headers
    usage = rate_limiter.get_usage(identifier, endpoint_type="ai")
    response.headers["X-RateLimit-Limit"] = str(usage["limit"])
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(reset_in)


class RateLimitDepends:
    """
    Configurable rate limit dependency.

    Usage:
        @app.get("/endpoint", dependencies=[Depends(RateLimitDepends(limit=10, window=60))])
    """

    def __init__(
        self,
        limit: Optional[int] = None,
        window_seconds: Optional[int] = None,
        endpoint_type: str = "default",
    ):
        self.limit = limit
        self.window_seconds = window_seconds
        self.endpoint_type = endpoint_type

    async def __call__(
        self,
        request: Request,
        response: Response,
        user: Optional[CurrentUser] = Depends(get_current_user_optional),
    ):
        identifier = _get_identifier(request, user)
        remaining, reset_in = rate_limiter.check_or_raise(
            identifier,
            limit=self.limit,
            window_seconds=self.window_seconds,
            endpoint_type=self.endpoint_type,
        )

        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_in)
