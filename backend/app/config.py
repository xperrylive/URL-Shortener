"""
Application Settings.

Loaded from environment variables (or .env file) via pydantic-settings.
Access settings anywhere with: from app.config import settings
"""
from functools import lru_cache

from pydantic import AnyUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Database ─────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/urlshortener"

    # ── Redis ─────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379"

    # ── JWT / Auth ────────────────────────────────────────────────
    secret_key: str = "changeme-generate-with-secrets-token-hex-32"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # ── Application ───────────────────────────────────────────────
    base_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    environment: str = "development"

    # ── GeoIP ─────────────────────────────────────────────────────
    geoip_db_path: str = "/app/GeoLite2-City.mmdb"

    # ── CORS ──────────────────────────────────────────────────────
    # Comma-separated list of allowed origins
    cors_origins: str = "http://localhost:3000"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v: str) -> str:
        return v  # kept as raw string; split on use

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (created once per process)."""
    return Settings()


# Module-level singleton — import this everywhere
settings = get_settings()
