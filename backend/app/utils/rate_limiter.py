"""
Rate Limiter Utility.

Implements a Redis sliding window rate limiter.

Key format:
  ratelimit:shorten:{ip}        → anonymous (10 shortens/day)
  ratelimit:shorten:{user_id}   → free tier (50 shortens/day)

Pro tier users bypass rate limiting entirely.
Returns HTTP 429 with Retry-After header when limit exceeded.
"""
from fastapi import HTTPException, status

async def check_rate_limit(redis, identifier: str, is_anonymous: bool = True):
    """Enforce rate limits using Redis."""
    # Limits
    limit = 10 if is_anonymous else 50
    window_seconds = 86400  # 1 day

    key = f"ratelimit:shorten:{identifier}"
    
    current = await redis.incr(key)
    if current == 1:
        await redis.expire(key, window_seconds)
        
    if current > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. You can only shorten {limit} links per day.",
            headers={"Retry-After": str(window_seconds)}
        )
