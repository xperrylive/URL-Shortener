"""
User ORM Model.

Schema:
    id            UUID PK (server default: gen_random_uuid())
    email         VARCHAR(255) UNIQUE NOT NULL
    password_hash VARCHAR(255) NOT NULL
    api_key       VARCHAR(64) UNIQUE nullable
    tier          ENUM('free', 'pro') DEFAULT 'free'
    is_active     BOOLEAN DEFAULT true
    created_at    TIMESTAMP DEFAULT now()
    updated_at    TIMESTAMP DEFAULT now()
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserTier(str):
    FREE = "free"
    PRO = "pro"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    api_key: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    tier: Mapped[str] = mapped_column(
        Enum("free", "pro", name="user_tier_enum"),
        nullable=False,
        default="free",
        server_default="free",
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ── Relationships ──────────────────────────────────────────────
    urls: Mapped[list["URL"]] = relationship("URL", back_populates="user", lazy="noload")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} tier={self.tier}>"
