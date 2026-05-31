"""
Redirect Router.

Endpoints:
  GET /{short_code} → Redirect to original URL, log click

Redirect Flow:
  1. Check Redis cache (url:{short_code})
  2. Cache miss → query Postgres
  3. 404 if not found / inactive; 410 if expired
  4. Cache result (TTL=3600s)
  5. 301 redirect to original URL
  6. Fire BackgroundTask to log click
"""
