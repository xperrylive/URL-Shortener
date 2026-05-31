"""
JWT Utilities.

Creates and verifies access and refresh tokens using python-jose.

Token payload structure:
    {
        "sub":  "<user_id as str>",
        "type": "access" | "refresh",
        "exp":  <unix timestamp>,
        "iat":  <unix timestamp>,
    }
"""
from datetime import datetime, timedelta, timezone
from typing import Literal

from jose import JWTError, jwt

from app.config import settings

# ── Token Types ───────────────────────────────────────────────────────────────
TokenType = Literal["access", "refresh"]


def _build_payload(
    subject: str,
    token_type: TokenType,
    expires_delta: timedelta,
) -> dict:
    now = datetime.now(timezone.utc)
    return {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }


# ── Creation ──────────────────────────────────────────────────────────────────

def create_access_token(subject: str) -> str:
    """Create a short-lived access token (30 min by default)."""
    payload = _build_payload(
        subject=subject,
        token_type="access",
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(subject: str) -> str:
    """Create a long-lived refresh token (7 days by default)."""
    payload = _build_payload(
        subject=subject,
        token_type="refresh",
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
    )
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


# ── Verification ──────────────────────────────────────────────────────────────

def verify_token(token: str, expected_type: TokenType = "access") -> dict:
    """Decode and validate a JWT token.

    Returns the decoded payload dict on success.
    Raises jose.JWTError on any failure (expired, wrong type, bad signature, etc.).
    """
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

    if payload.get("type") != expected_type:
        raise JWTError(f"Invalid token type: expected '{expected_type}'")

    return payload


def get_subject(token: str, expected_type: TokenType = "access") -> str:
    """Convenience wrapper — returns the 'sub' claim (user_id as str)."""
    payload = verify_token(token, expected_type)
    sub = payload.get("sub")
    if not sub:
        raise JWTError("Token missing 'sub' claim")
    return sub
