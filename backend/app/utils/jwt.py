"""
JWT Utilities.

Provides:
  - create_access_token(data, expires_delta)   → signed JWT string
  - create_refresh_token(data)                 → signed JWT string (7-day)
  - verify_token(token)                        → decoded payload dict
"""
