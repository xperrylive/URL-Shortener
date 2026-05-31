"""
Alembic environment script — runs migrations against the async PostgreSQL engine.

Key points:
- DATABASE_URL is read from app.config (which reads from .env) — never hardcoded
- Uses SQLAlchemy async engine via run_sync for the migration context
- target_metadata points to Base.metadata so autogenerate works
"""
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# ── Alembic Config ────────────────────────────────────────────────────────────
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Import all models so Alembic autogenerate can see them ────────────────────
# This import chain ensures Base.metadata has all table definitions registered.
from app.database import Base  # noqa: E402
from app.models import User, URL, Click  # noqa: E402, F401

target_metadata = Base.metadata

# ── Override sqlalchemy.url from our settings (.env) ─────────────────────────
from app.config import settings  # noqa: E402

# Convert asyncpg URL to sync psycopg2 format for Alembic's run_migrations_online
# (Alembic itself uses sync connections; our app uses async)
_sync_url = settings.database_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
config.set_main_option("sqlalchemy.url", _sync_url)


# ── Offline Migrations ────────────────────────────────────────────────────────
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (generate SQL without a DB connection)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Online Migrations ─────────────────────────────────────────────────────────
def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations through a sync connection."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        # Use the asyncpg URL for the async engine
        url=settings.database_url,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
