"""
Cache Service.

Redis get/set/delete wrappers for URL caching.

Key convention:
  url:{short_code}  →  original_url string (TTL: 3600s)
"""
