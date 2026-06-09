"""
Caching layer with Redis support and in-memory fallback.
"""

import hashlib
import json
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Optional, TypeVar

from .config import settings
from .logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class CacheBackend(ABC):
    """Abstract cache backend interface."""

    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """Get a value from cache."""
        pass

    @abstractmethod
    async def set(self, key: str, value: str, ttl: int) -> bool:
        """Set a value in cache with TTL in seconds."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        pass

    @abstractmethod
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching a pattern. Returns count of deleted keys."""
        pass


class InMemoryCache(CacheBackend):
    """Simple in-memory cache for development/single-instance deployments."""

    def __init__(self):
        self._cache: dict[str, tuple[str, float]] = {}
        self._cleanup_interval = 60  # seconds
        self._last_cleanup = time.time()

    def _cleanup(self):
        """Remove expired entries."""
        now = time.time()
        if now - self._last_cleanup < self._cleanup_interval:
            return

        expired_keys = [
            key for key, (_, expiry) in self._cache.items()
            if expiry < now
        ]
        for key in expired_keys:
            del self._cache[key]

        self._last_cleanup = now

    async def get(self, key: str) -> Optional[str]:
        self._cleanup()
        if key in self._cache:
            value, expiry = self._cache[key]
            if expiry > time.time():
                return value
            else:
                del self._cache[key]
        return None

    async def set(self, key: str, value: str, ttl: int) -> bool:
        self._cache[key] = (value, time.time() + ttl)
        return True

    async def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    async def exists(self, key: str) -> bool:
        self._cleanup()
        if key in self._cache:
            _, expiry = self._cache[key]
            return expiry > time.time()
        return False

    async def clear_pattern(self, pattern: str) -> int:
        """Clear keys matching pattern. Simple wildcard support."""
        import fnmatch
        matching_keys = [
            key for key in self._cache.keys()
            if fnmatch.fnmatch(key, pattern)
        ]
        for key in matching_keys:
            del self._cache[key]
        return len(matching_keys)


class RedisCache(CacheBackend):
    """Redis cache backend for production."""

    def __init__(self, redis_url: str):
        try:
            import redis.asyncio as redis
            self._redis = redis.from_url(redis_url, decode_responses=True)
            self._available = True
        except ImportError:
            logger.warning("Redis library not installed, falling back to in-memory cache")
            self._available = False
            self._fallback = InMemoryCache()

    async def get(self, key: str) -> Optional[str]:
        if not self._available:
            return await self._fallback.get(key)
        try:
            return await self._redis.get(key)
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None

    async def set(self, key: str, value: str, ttl: int) -> bool:
        if not self._available:
            return await self._fallback.set(key, value, ttl)
        try:
            await self._redis.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        if not self._available:
            return await self._fallback.delete(key)
        try:
            result = await self._redis.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            return False

    async def exists(self, key: str) -> bool:
        if not self._available:
            return await self._fallback.exists(key)
        try:
            return await self._redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis EXISTS error: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        if not self._available:
            return await self._fallback.clear_pattern(pattern)
        try:
            keys = []
            async for key in self._redis.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                await self._redis.delete(*keys)
            return len(keys)
        except Exception as e:
            logger.error(f"Redis CLEAR_PATTERN error: {e}")
            return 0


class CacheService:
    """High-level caching service with serialization and key management."""

    def __init__(self):
        if settings.redis_url:
            self._backend = RedisCache(settings.redis_url)
        else:
            self._backend = InMemoryCache()

        self._prefix = "career_api"

    def _make_key(self, namespace: str, key: str) -> str:
        """Create a namespaced cache key."""
        return f"{self._prefix}:{namespace}:{key}"

    def _hash_key(self, data: Any) -> str:
        """Create a hash from any data to use as cache key."""
        if isinstance(data, str):
            content = data
        else:
            content = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(content.encode()).hexdigest()[:16]

    async def get(self, namespace: str, key: str) -> Optional[Any]:
        """Get a cached value, deserializing JSON."""
        full_key = self._make_key(namespace, key)
        value = await self._backend.get(full_key)
        if value is not None:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(
        self,
        namespace: str,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """Set a cached value, serializing to JSON."""
        full_key = self._make_key(namespace, key)
        ttl = ttl or settings.cache_ttl_seconds

        if isinstance(value, str):
            serialized = value
        else:
            serialized = json.dumps(value, default=str)

        return await self._backend.set(full_key, serialized, ttl)

    async def delete(self, namespace: str, key: str) -> bool:
        """Delete a cached value."""
        full_key = self._make_key(namespace, key)
        return await self._backend.delete(full_key)

    async def clear_namespace(self, namespace: str) -> int:
        """Clear all cached values in a namespace."""
        pattern = self._make_key(namespace, "*")
        return await self._backend.clear_pattern(pattern)

    async def get_or_set(
        self,
        namespace: str,
        key: str,
        factory: Callable[[], Any],
        ttl: Optional[int] = None,
    ) -> Any:
        """Get cached value or compute and cache it."""
        cached = await self.get(namespace, key)
        if cached is not None:
            logger.debug(f"Cache hit: {namespace}:{key}")
            return cached

        logger.debug(f"Cache miss: {namespace}:{key}")
        value = await factory() if callable(factory) else factory
        await self.set(namespace, key, value, ttl)
        return value


# Cache namespaces for different features
class CacheNamespace:
    ROADMAP = "roadmap"
    RESUME_ANALYSIS = "resume"
    SKILL_GAP = "skill_gap"
    JOB_SEARCH = "jobs"
    CAREER_DATA = "career"
    CONVERSATION = "conversation"
    USER_PROFILE = "user"


# Global cache instance
cache = CacheService()


# Decorator for caching function results
def cached(
    namespace: str,
    ttl: Optional[int] = None,
    key_builder: Optional[Callable[..., str]] = None,
):
    """
    Decorator to cache async function results.

    Usage:
        @cached(CacheNamespace.ROADMAP, ttl=86400)
        async def generate_roadmap(career_field: str, skills: list) -> dict:
            ...
    """
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                key_data = {"args": args, "kwargs": kwargs}
                cache_key = cache._hash_key(key_data)

            # Try to get from cache
            cached_value = await cache.get(namespace, cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            await cache.set(namespace, cache_key, result, ttl)
            logger.debug(f"Cached result for {func.__name__}")

            return result

        return wrapper
    return decorator
