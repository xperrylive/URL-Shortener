"""
URL ORM Model.

Schema:
    id           UUID PK
    original_url TEXT NOT NULL
    short_code   VARCHAR(20) UNIQUE NOT NULL  [INDEXED — redirect hotpath]
    custom_alias VARCHAR(50) UNIQUE nullable
    user_id      UUID FK → users.id nullable  (anonymous shortens allowed)
    is_active    BOOLEAN DEFAULT true
    expires_at   TIMESTAMP nullable
    click_count  INTEGER DEFAULT 0
    created_at   TIMESTAMP DEFAULT now()
    updated_at   TIMESTAMP DEFAULT now()
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class URL(Base):
    __tablename__ = "urls"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    original_url: Mapped[str] = mapped_column(Text, nullable=False)
    short_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    custom_alias: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    click_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
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
    user: Mapped["User | None"] = relationship("User", back_populates="urls", lazy="noload")
    clicks: Mapped[list["Click"]] = relationship("Click", back_populates="url", lazy="noload")

    def __repr__(self) -> str:
        return f"<URL short_code={self.short_code} active={self.is_active}>"
