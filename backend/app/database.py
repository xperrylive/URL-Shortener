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
engine_kwargs = {}
if "postgresql" in settings.database_url:
    engine_kwargs.update({
        "pool_size": 5,
        "max_overflow": 10,
        "pool_pre_ping": True,
    })
elif "sqlite" in settings.database_url:
    engine_kwargs.update({
        "connect_args": {"check_same_thread": False}
    })

engine = create_async_engine(
    settings.database_url,
    # Echo SQL in development only; never in production
    echo=not settings.is_production,
    **engine_kwargs
)

# Enable foreign keys for SQLite
if "sqlite" in settings.database_url:
    from sqlalchemy import event
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

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
