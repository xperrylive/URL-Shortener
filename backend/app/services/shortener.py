"""
Shortener Service.

Provides:
  - generate_short_code(db)        → unique 6-char base62 code (up to 3 retries)
  - validate_custom_alias(alias)   → raises ValueError on invalid aliases
  - build_short_url(short_code)    → full short URL string
"""
import hashlib
import os
import re
import time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.url import URL

# ── Constants ─────────────────────────────────────────────────────────────────

_BASE62_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
_CODE_LENGTH = 6
_MAX_RETRIES = 3

RESERVED_WORDS: frozenset[str] = frozenset({
    "api", "admin", "dashboard", "login", "register", "logout",
    "health", "docs", "redoc", "static", "favicon",
})

_ALIAS_PATTERN = re.compile(r"^[a-zA-Z0-9\-]{3,50}$")


# ── Base62 Encoding ───────────────────────────────────────────────────────────

def _to_base62(n: int, length: int = _CODE_LENGTH) -> str:
    """Convert an integer to a base62 string of a fixed length."""
    result = []
    for _ in range(length):
        result.append(_BASE62_CHARS[n % 62])
        n //= 62
    return "".join(reversed(result))


def _generate_candidate(original_url: str, salt: bytes | None = None) -> str:
    """Generate one candidate short code from a URL + random salt."""
    if salt is None:
        salt = os.urandom(8)
    payload = f"{original_url}{time.time_ns()}".encode() + salt
    digest = int(hashlib.sha256(payload).hexdigest(), 16)
    return _to_base62(digest)


# ── Public API ────────────────────────────────────────────────────────────────

async def generate_short_code(db: AsyncSession, original_url: str) -> str:
    """Generate a unique 6-character base62 short code.

    Performs a DB collision check and retries up to _MAX_RETRIES times.
    Raises RuntimeError if all retries are exhausted (astronomically unlikely).
    """
    for attempt in range(_MAX_RETRIES):
        candidate = _generate_candidate(original_url, salt=os.urandom(attempt + 4))
        result = await db.execute(
            select(URL.id).where(URL.short_code == candidate)
        )
        if result.scalar_one_or_none() is None:
            return candidate  # unique — we're done

    raise RuntimeError(
        f"Failed to generate a unique short code after {_MAX_RETRIES} attempts. "
        "This should not happen in practice."
    )


def validate_custom_alias(alias: str) -> str:
    """Validate a user-supplied custom alias.

    Returns the alias unchanged on success.
    Raises ValueError with a descriptive message on failure.
    """
    if not _ALIAS_PATTERN.match(alias):
        raise ValueError(
            "Custom alias must be 3–50 characters, using only letters, digits, and hyphens."
        )
    if alias.lower() in RESERVED_WORDS:
        raise ValueError(f"'{alias}' is a reserved word and cannot be used as a custom alias.")
    return alias


def build_short_url(short_code: str) -> str:
    """Construct the full short URL from a short code."""
    base = settings.base_url.rstrip("/")
    return f"{base}/{short_code}"
