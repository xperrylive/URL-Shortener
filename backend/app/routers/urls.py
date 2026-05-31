"""
URLs Router.

Endpoints:
  POST   /api/urls/shorten         → Create a short URL
  GET    /api/urls/                → List authenticated user's URLs
  GET    /api/urls/{short_code}    → Get URL details
  PATCH  /api/urls/{short_code}    → Update alias or expiry
  DELETE /api/urls/{short_code}    → Deactivate a URL
"""
