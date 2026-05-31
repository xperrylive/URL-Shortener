"""
Pytest configuration and shared fixtures.

Uses httpx.AsyncClient against the FastAPI app with:
  - In-memory SQLite (for speed, schema-compatible with SQLAlchemy)
  - Fake Redis (fakeredis) if available, else real local Redis
"""
import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base
from app.dependencies import get_db, get_redis
from app.main import app

# ── In-memory SQLite engine (fast, no external DB required) ──────────────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSession = async_sessionmaker(test_engine, expire_on_commit=False)


async def _get_test_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSession() as session:
        yield session


# ── Fake Redis ────────────────────────────────────────────────────────────────
try:
    import fakeredis.aioredis as fake_redis  # type: ignore

    async def _get_fake_redis():
        return fake_redis.FakeRedis(decode_responses=True)
    _redis_override = _get_fake_redis
except ImportError:
    import redis.asyncio as aioredis

    async def _get_real_redis():
        return aioredis.from_url("redis://localhost:6379", decode_responses=True)
    _redis_override = _get_real_redis


# ── App dependency overrides ──────────────────────────────────────────────────
app.dependency_overrides[get_db] = _get_test_db
app.dependency_overrides[get_redis] = _redis_override


# ── Session-scoped fixtures ───────────────────────────────────────────────────
@pytest.fixture(scope="session")
def event_loop():
    """Use a single event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_tables():
    """Create all tables once before tests run, drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client bound to the FastAPI test app."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


# ── Reusable user helpers ─────────────────────────────────────────────────────
@pytest_asyncio.fixture
async def registered_user(client: AsyncClient) -> dict:
    """Register a fresh user and return the AuthResponse payload."""
    resp = await client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "TestPass1"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest_asyncio.fixture
async def auth_headers(registered_user: dict) -> dict:
    """Return Authorization headers for the registered user."""
    token = registered_user["access_token"]
    return {"Authorization": f"Bearer {token}"}
