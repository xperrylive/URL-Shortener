"""
Pytest configuration and shared fixtures.

Uses httpx.AsyncClient against the FastAPI app with:
  - In-memory SQLite (for speed, schema-compatible with SQLAlchemy)
  - fakeredis (in-memory Redis substitute, no external server required)
  - Per-test DB isolation via table truncation after each test
"""
import uuid
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base
from app.dependencies import get_db, get_redis
from app.main import app

# ── In-memory SQLite engine ───────────────────────────────────────────────────
# SQLite doesn't support multiple tables in one CREATE ENUM statement,
# so we disable the Postgres-specific ENUM types via SQLite's fallback mode.
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)
TestSession: async_sessionmaker[AsyncSession] = async_sessionmaker(
    test_engine, expire_on_commit=False
)


async def _get_test_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSession() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


# ── Fake Redis ────────────────────────────────────────────────────────────────
try:
    import fakeredis.aioredis as _fakeredis  # type: ignore

    _fake_redis_server = _fakeredis.FakeServer()

    async def _get_fake_redis():
        return _fakeredis.FakeRedis(server=_fake_redis_server, decode_responses=True)

except ImportError:
    import redis.asyncio as aioredis

    async def _get_fake_redis():  # type: ignore[misc]
        return aioredis.from_url("redis://localhost:6379", decode_responses=True)


# ── Dependency overrides ──────────────────────────────────────────────────────
app.dependency_overrides[get_db] = _get_test_db
app.dependency_overrides[get_redis] = _get_fake_redis


# ── Schema creation / teardown (session-scoped) ───────────────────────────────
@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_tables():
    """Create all tables once for the session, drop on teardown."""
    async with test_engine.begin() as conn:
        # SQLite doesn't have gen_random_uuid() or ENUM types.
        # SQLAlchemy renders them transparently for SQLite, but we need to
        # let it handle the dialect differences automatically.
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ── Per-test DB isolation ─────────────────────────────────────────────────────
@pytest_asyncio.fixture(autouse=True)
async def clean_db():
    """Truncate all tables before each test for full isolation."""
    yield
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())



# ── HTTP client ───────────────────────────────────────────────────────────────
@pytest_asyncio.fixture(scope="session", autouse=True)
async def patch_log_click():
    """Patch _log_click in the redirect router to use the SQLite test engine.

    _log_click creates its own DB session using the production engine, which
    isn't running during tests. We replace it with a version that uses TestSession.
    """
    import app.routers.redirect as redirect_module
    original = redirect_module._log_click

    async def _test_log_click(short_code: str, session_factory=None):
        await original(short_code, session_factory=TestSession)

    redirect_module._log_click = _test_log_click
    yield
    redirect_module._log_click = original


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


# ── Reusable auth helpers ─────────────────────────────────────────────────────
@pytest_asyncio.fixture
async def registered_user(client: AsyncClient) -> dict:
    """Register a fresh user with a unique email and return the AuthResponse."""
    unique_email = f"user-{uuid.uuid4().hex[:8]}@test.com"
    resp = await client.post(
        "/api/auth/register",
        json={"email": unique_email, "password": "TestPass1"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest_asyncio.fixture
async def auth_headers(registered_user: dict) -> dict:
    """Return Authorization headers for the registered user."""
    return {"Authorization": f"Bearer {registered_user['access_token']}"}
