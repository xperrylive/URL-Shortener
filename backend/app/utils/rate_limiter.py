"""
Rate Limiter Utility.

Implements a Redis sliding window rate limiter.

Key format:
  ratelimit:shorten:{ip}        → anonymous (10 shortens/day)
  ratelimit:shorten:{user_id}   → free tier (50 shortens/day)

Pro tier users bypass rate limiting entirely.
Returns HTTP 429 with Retry-After header when limit exceeded.
"""
