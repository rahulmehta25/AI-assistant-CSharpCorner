"""
Rate limiting implementation with sliding window algorithm.
"""

import time
from typing import Optional

from .config import settings
from .exceptions import RateLimitError
from .logging import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """
    Rate limiter using sliding window algorithm.
    Supports both in-memory and Redis backends.
    """

    def __init__(self):
        self._storage: dict[str, list[float]] = {}
        self._redis = None

        if settings.redis_url:
            try:
                import redis
                self._redis = redis.from_url(settings.redis_url)
            except ImportError:
                logger.warning("Redis not available, using in-memory rate limiting")

    def _clean_old_requests(self, key: str, window_start: float) -> list[float]:
        """Remove requests older than the window."""
        if key not in self._storage:
            return []
        self._storage[key] = [
            ts for ts in self._storage[key]
            if ts > window_start
        ]
        return self._storage[key]

    def check_rate_limit(
        self,
        identifier: str,
        limit: Optional[int] = None,
        window_seconds: Optional[int] = None,
        endpoint_type: str = "default",
    ) -> tuple[bool, int, int]:
        """
        Check if request is within rate limit.

        Args:
            identifier: User ID, API key, or IP address
            limit: Max requests (defaults to settings)
            window_seconds: Window size (defaults to settings)
            endpoint_type: Type of endpoint (default/ai) for different limits

        Returns:
            Tuple of (allowed, remaining, reset_in_seconds)
        """
        if not settings.rate_limit_enabled:
            return True, 999, 0

        # Use different limits for AI endpoints
        if endpoint_type == "ai":
            limit = limit or settings.rate_limit_ai_requests
        else:
            limit = limit or settings.rate_limit_requests

        window_seconds = window_seconds or settings.rate_limit_window_seconds

        now = time.time()
        window_start = now - window_seconds
        key = f"ratelimit:{identifier}:{endpoint_type}"

        if self._redis:
            return self._check_redis(key, limit, window_seconds, now)
        else:
            return self._check_memory(key, limit, window_start, now, window_seconds)

    def _check_memory(
        self,
        key: str,
        limit: int,
        window_start: float,
        now: float,
        window_seconds: int,
    ) -> tuple[bool, int, int]:
        """In-memory rate limit check."""
        requests = self._clean_old_requests(key, window_start)
        current_count = len(requests)

        if current_count >= limit:
            # Find when the oldest request will expire
            oldest = min(requests) if requests else now
            reset_in = int(oldest + window_seconds - now)
            return False, 0, max(1, reset_in)

        # Add current request
        if key not in self._storage:
            self._storage[key] = []
        self._storage[key].append(now)

        remaining = limit - current_count - 1
        return True, remaining, window_seconds

    def _check_redis(
        self,
        key: str,
        limit: int,
        window_seconds: int,
        now: float,
    ) -> tuple[bool, int, int]:
        """Redis-backed rate limit check using sorted set."""
        try:
            pipe = self._redis.pipeline()

            # Remove old entries
            window_start = now - window_seconds
            pipe.zremrangebyscore(key, 0, window_start)

            # Count current requests
            pipe.zcard(key)

            # Add current request (score = timestamp)
            pipe.zadd(key, {str(now): now})

            # Set expiry on the key
            pipe.expire(key, window_seconds)

            results = pipe.execute()
            current_count = results[1]

            if current_count >= limit:
                # Get oldest timestamp
                oldest = self._redis.zrange(key, 0, 0, withscores=True)
                if oldest:
                    oldest_ts = oldest[0][1]
                    reset_in = int(oldest_ts + window_seconds - now)
                else:
                    reset_in = window_seconds
                return False, 0, max(1, reset_in)

            remaining = limit - current_count - 1
            return True, remaining, window_seconds

        except Exception as e:
            logger.error(f"Redis rate limit error: {e}")
            # Fail open - allow the request but log the error
            return True, limit - 1, window_seconds

    def is_allowed(
        self,
        identifier: str,
        limit: Optional[int] = None,
        window_seconds: Optional[int] = None,
        endpoint_type: str = "default",
    ) -> bool:
        """Simple check that returns True/False."""
        allowed, _, _ = self.check_rate_limit(
            identifier, limit, window_seconds, endpoint_type
        )
        return allowed

    def check_or_raise(
        self,
        identifier: str,
        limit: Optional[int] = None,
        window_seconds: Optional[int] = None,
        endpoint_type: str = "default",
    ) -> tuple[int, int]:
        """
        Check rate limit and raise RateLimitError if exceeded.

        Returns:
            Tuple of (remaining, reset_in_seconds)
        """
        allowed, remaining, reset_in = self.check_rate_limit(
            identifier, limit, window_seconds, endpoint_type
        )

        if not allowed:
            raise RateLimitError(
                message="Rate limit exceeded. Please wait before making more requests.",
                retry_after=reset_in,
            )

        return remaining, reset_in

    def get_usage(self, identifier: str, endpoint_type: str = "default") -> dict:
        """Get current usage stats for an identifier."""
        if endpoint_type == "ai":
            limit = settings.rate_limit_ai_requests
        else:
            limit = settings.rate_limit_requests

        window_seconds = settings.rate_limit_window_seconds

        _, remaining, reset_in = self.check_rate_limit(
            identifier,
            limit=limit + 1,  # Add 1 to not consume a request
            window_seconds=window_seconds,
            endpoint_type=endpoint_type,
        )

        return {
            "limit": limit,
            "remaining": remaining,
            "reset_in_seconds": reset_in,
            "window_seconds": window_seconds,
        }


# Global rate limiter instance
rate_limiter = RateLimiter()
