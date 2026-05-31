"""
Auth Pydantic Schemas (v2).

Request/response models for authentication endpoints.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


# ── Request Schemas ───────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128, description="Minimum 8 characters")

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """Body is optional — refresh token is read from httpOnly cookie first."""
    refresh_token: str | None = None


# ── Response Schemas ──────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until access token expires


class UserResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    email: str
    tier: str
    is_active: bool
    created_at: datetime


class AuthResponse(BaseModel):
    """Returned on successful login / register."""
    user: UserResponse
    access_token: str
    token_type: str = "bearer"
    expires_in: int
