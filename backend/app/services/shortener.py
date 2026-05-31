"""
Shortener Service.

Provides:
  - generate_short_code()    → 6-char base62 code (collision-safe, max 3 retries)
  - validate_custom_alias()  → 3–30 chars, alphanumeric + hyphens, no reserved words
"""

RESERVED_WORDS = {"api", "admin", "dashboard", "login", "register", "logout", "health"}
