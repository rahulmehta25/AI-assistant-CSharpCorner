"""
Redis Caching Service for AI Responses
Provides caching for career advice, roadmap generation, and resume analysis
"""

import hashlib
import json
import os
from datetime import timedelta
from typing import Any, Optional, Callable
from functools import wraps

import redis
from redis.exceptions import RedisError


class CacheService:
    """Redis-based caching service for AI responses"""

    # Cache TTL configurations (in seconds)
    TTL_CONFIG = {
        "career_advice": 3600 * 24,      # 24 hours
        "roadmap": 3600 * 24 * 7,         # 7 days
        "resume_analysis": 3600 * 12,     # 12 hours
        "skill_gap": 3600 * 24,           # 24 hours
        "job_match": 3600 * 6,            # 6 hours
        "cover_letter": 3600 * 24,        # 24 hours
        "interview_prep": 3600 * 24 * 3,  # 3 days
        "session": 3600 * 24,             # 24 hours
        "default": 3600,                  # 1 hour
    }

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._client: Optional[redis.Redis] = None
        self._connected = False

    @property
    def client(self) -> redis.Redis:
        """Get or create Redis client with lazy initialization"""
        if self._client is None:
            try:
                self._client = redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                )
                # Test connection
                self._client.ping()
                self._connected = True
            except RedisError as e:
                print(f"Redis connection failed: {e}")
                self._connected = False
                raise
        return self._client

    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        try:
            if self._client:
                self._client.ping()
                self._connected = True
            return self._connected
        except (RedisError, AttributeError):
            self._connected = False
            return False

    def _generate_key(self, cache_type: str, *args, **kwargs) -> str:
        """Generate a unique cache key based on inputs"""
        key_data = {
            "type": cache_type,
            "args": args,
            "kwargs": kwargs,
        }
        key_hash = hashlib.sha256(
            json.dumps(key_data, sort_keys=True, default=str).encode()
        ).hexdigest()[:16]
        return f"career:{cache_type}:{key_hash}"

    def _get_ttl(self, cache_type: str) -> int:
        """Get TTL for a cache type"""
        return self.TTL_CONFIG.get(cache_type, self.TTL_CONFIG["default"])

    async def get(self, cache_type: str, *args, **kwargs) -> Optional[Any]:
        """
        Get cached value

        Args:
            cache_type: Type of cache (e.g., 'career_advice', 'roadmap')
            *args, **kwargs: Parameters used to generate the cache key

        Returns:
            Cached value or None if not found
        """
        try:
            key = self._generate_key(cache_type, *args, **kwargs)
            value = self.client.get(key)

            if value:
                # Update access statistics
                self.client.hincrby(f"{key}:stats", "hits", 1)
                return json.loads(value)

            return None
        except (RedisError, json.JSONDecodeError) as e:
            print(f"Cache get error: {e}")
            return None

    async def set(
        self,
        cache_type: str,
        value: Any,
        *args,
        ttl: Optional[int] = None,
        **kwargs
    ) -> bool:
        """
        Set cached value

        Args:
            cache_type: Type of cache
            value: Value to cache
            *args, **kwargs: Parameters used to generate the cache key
            ttl: Optional custom TTL in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            key = self._generate_key(cache_type, *args, **kwargs)
            ttl = ttl or self._get_ttl(cache_type)

            serialized = json.dumps(value, default=str)
            self.client.setex(key, ttl, serialized)

            # Store metadata
            self.client.hset(f"{key}:stats", mapping={
                "type": cache_type,
                "created_at": json.dumps({"$date": "now"}),
                "ttl": ttl,
            })

            return True
        except (RedisError, TypeError) as e:
            print(f"Cache set error: {e}")
            return False

    async def delete(self, cache_type: str, *args, **kwargs) -> bool:
        """Delete cached value"""
        try:
            key = self._generate_key(cache_type, *args, **kwargs)
            self.client.delete(key, f"{key}:stats")
            return True
        except RedisError as e:
            print(f"Cache delete error: {e}")
            return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching a pattern

        Args:
            pattern: Redis key pattern (e.g., 'career:roadmap:*')

        Returns:
            Number of keys deleted
        """
        try:
            keys = self.client.keys(f"career:{pattern}")
            if keys:
                return self.client.delete(*keys)
            return 0
        except RedisError as e:
            print(f"Cache invalidate error: {e}")
            return 0

    async def get_or_set(
        self,
        cache_type: str,
        generator: Callable,
        *args,
        ttl: Optional[int] = None,
        **kwargs
    ) -> Any:
        """
        Get from cache or generate and cache if not found

        Args:
            cache_type: Type of cache
            generator: Async function to generate value if not cached
            *args, **kwargs: Parameters for cache key and generator
            ttl: Optional custom TTL

        Returns:
            Cached or generated value
        """
        # Try to get from cache
        cached = await self.get(cache_type, *args, **kwargs)
        if cached is not None:
            return cached

        # Generate new value
        if callable(generator):
            import asyncio
            if asyncio.iscoroutinefunction(generator):
                value = await generator(*args, **kwargs)
            else:
                value = generator(*args, **kwargs)
        else:
            value = generator

        # Cache the result
        await self.set(cache_type, value, *args, ttl=ttl, **kwargs)

        return value

    # Session management
    async def set_session(self, session_id: str, data: dict, ttl: int = 86400) -> bool:
        """Store session data"""
        try:
            key = f"career:session:{session_id}"
            self.client.setex(key, ttl, json.dumps(data, default=str))
            return True
        except RedisError as e:
            print(f"Session set error: {e}")
            return False

    async def get_session(self, session_id: str) -> Optional[dict]:
        """Retrieve session data"""
        try:
            key = f"career:session:{session_id}"
            value = self.client.get(key)
            return json.loads(value) if value else None
        except (RedisError, json.JSONDecodeError):
            return None

    async def delete_session(self, session_id: str) -> bool:
        """Delete session data"""
        try:
            key = f"career:session:{session_id}"
            self.client.delete(key)
            return True
        except RedisError:
            return False

    # Rate limiting
    async def check_rate_limit(
        self,
        identifier: str,
        limit: int = 100,
        window: int = 3600
    ) -> tuple[bool, int]:
        """
        Check rate limit for an identifier

        Args:
            identifier: User ID or IP address
            limit: Maximum requests per window
            window: Time window in seconds

        Returns:
            Tuple of (allowed, remaining_requests)
        """
        try:
            key = f"career:ratelimit:{identifier}"

            current = self.client.get(key)
            if current is None:
                self.client.setex(key, window, 1)
                return True, limit - 1

            count = int(current)
            if count >= limit:
                return False, 0

            self.client.incr(key)
            return True, limit - count - 1
        except RedisError:
            # Allow on Redis error
            return True, limit

    # Statistics
    async def get_stats(self) -> dict:
        """Get cache statistics"""
        try:
            info = self.client.info()
            keys_count = self.client.dbsize()

            return {
                "connected": True,
                "keys_count": keys_count,
                "memory_used": info.get("used_memory_human", "N/A"),
                "uptime_days": info.get("uptime_in_days", 0),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
            }
        except RedisError as e:
            return {"connected": False, "error": str(e)}


# Singleton instance
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """Get the global cache service instance"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service


def cached(cache_type: str, ttl: Optional[int] = None):
    """
    Decorator for caching function results

    Usage:
        @cached("career_advice", ttl=3600)
        async def get_career_advice(user_profile: dict) -> dict:
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = get_cache_service()

            # Skip caching if Redis is not available
            if not cache.is_connected:
                import asyncio
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                return func(*args, **kwargs)

            return await cache.get_or_set(
                cache_type,
                func,
                *args,
                ttl=ttl,
                **kwargs
            )
        return wrapper
    return decorator
