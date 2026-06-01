"""
URL Pydantic Schemas (v2).

Request/response models for URL shortening and management endpoints.
"""
import uuid
from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, Field, field_validator


# ── Request Schemas ───────────────────────────────────────────────────────────

class ShortenRequest(BaseModel):
    url: AnyHttpUrl = Field(description="The long URL to shorten")
    custom_alias: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9\-]+$",
        description="Optional custom alias (alphanumeric + hyphens)",
    )
    expires_at: datetime | None = Field(
        default=None,
        description="Optional expiration timestamp (UTC)",
    )

    @field_validator("custom_alias")
    @classmethod
    def no_reserved_words(cls, v: str | None) -> str | None:
        if v is None:
            return v
        reserved = {"api", "admin", "dashboard", "login", "register", "logout", "health", "docs", "redoc"}
        if v.lower() in reserved:
            raise ValueError(f"'{v}' is a reserved word and cannot be used as a custom alias")
        return v


class UpdateURLRequest(BaseModel):
    custom_alias: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9\-]+$",
    )
    expires_at: datetime | None = None
    is_active: bool | None = None


# ── Response Schemas ──────────────────────────────────────────────────────────

class URLResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    original_url: str
    short_code: str
    short_url: str  # full short URL e.g. https://domain.com/abc123
    custom_alias: str | None
    user_id: uuid.UUID | None
    is_active: bool
    expires_at: datetime | None
    click_count: int
    created_at: datetime
    updated_at: datetime


class URLListResponse(BaseModel):
    items: list[URLResponse]
    total: int
    total_active: int
    total_clicks: int
    page: int
    page_size: int
    pages: int
