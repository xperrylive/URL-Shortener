"""
Cache Service — Redis wrappers for URL caching.

Key convention:
    url:{short_code}  →  original_url string   TTL: 3600s
    url:{short_code}  →  "__INACTIVE__"         TTL: 300s  (negative cache)

This prevents DB hammering for non-existent or inactive short codes.
"""
import redis.asyncio as aioredis

_URL_TTL = 3600          # 1 hour for active URLs
_INACTIVE_TTL = 300      # 5 minutes for inactive/not-found codes
_INACTIVE_SENTINEL = "__INACTIVE__"


def _cache_key(short_code: str) -> str:
    return f"url:{short_code}"


async def get_cached_url(redis: aioredis.Redis, short_code: str) -> str | None:
    """Return the cached original URL, or None on cache miss.

    Returns the sentinel string "__INACTIVE__" if the URL is known to be
    inactive — callers should treat this as a 404/410 response.
    """
    return await redis.get(_cache_key(short_code))


async def set_cached_url(redis: aioredis.Redis, short_code: str, original_url: str) -> None:
    """Cache an active URL with full TTL."""
    await redis.set(_cache_key(short_code), original_url, ex=_URL_TTL)


async def set_inactive_cache(redis: aioredis.Redis, short_code: str) -> None:
    """Cache a negative result (not found / inactive) with a short TTL."""
    await redis.set(_cache_key(short_code), _INACTIVE_SENTINEL, ex=_INACTIVE_TTL)


async def invalidate_url_cache(redis: aioredis.Redis, short_code: str) -> None:
    """Remove a URL from the cache (call when a URL is updated/deleted)."""
    await redis.delete(_cache_key(short_code))


def is_inactive_sentinel(value: str) -> bool:
    return value == _INACTIVE_SENTINEL
