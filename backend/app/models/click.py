"""
Click ORM Model.

Schema:
    id          UUID PK
    url_id      UUID FK → urls.id  [INDEXED]
    ip_address  VARCHAR(45) nullable
    country     VARCHAR(100) nullable
    city        VARCHAR(100) nullable
    referrer    TEXT nullable
    user_agent  TEXT nullable
    device_type ENUM('mobile','desktop','bot','unknown') DEFAULT 'unknown'
    clicked_at  TIMESTAMP DEFAULT now()  [INDEXED — time-series queries]
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Click(Base):
    __tablename__ = "clicks"

    __table_args__ = (
        # Composite index on url_id + clicked_at supports time-series analytics per URL
        Index("ix_clicks_url_id_clicked_at", "url_id", "clicked_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    url_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("urls.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    referrer: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    device_type: Mapped[str] = mapped_column(
        Enum("mobile", "desktop", "bot", "unknown", name="device_type_enum"),
        nullable=False,
        default="unknown",
        server_default="unknown",
    )
    clicked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        index=True,
    )

    # ── Relationships ──────────────────────────────────────────────
    url: Mapped["URL"] = relationship("URL", back_populates="clicks", lazy="noload")

    def __repr__(self) -> str:
        return f"<Click url_id={self.url_id} device={self.device_type} at={self.clicked_at}>"
