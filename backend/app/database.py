"""
Async SQLAlchemy 2.0 Engine and Session Factory.

Usage (via dependency injection — prefer get_db from dependencies.py):

    async with async_session() as session:
        result = await session.execute(select(User))

All models must import Base from this module for Alembic autogenerate to work.
"""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# ── Engine ────────────────────────────────────────────────────────────────────
engine = create_async_engine(
    settings.database_url,
    # Echo SQL in development only; never in production
    echo=not settings.is_production,
    # Keep a small pool — suitable for Railway free tier
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,   # recycle stale connections silently
)

# ── Session Factory ───────────────────────────────────────────────────────────
async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # objects remain accessible after commit
    autoflush=False,
    autocommit=False,
)


# ── Declarative Base ──────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """All ORM models inherit from this base.

    Alembic target_metadata points here for autogenerate.
    """
    pass
