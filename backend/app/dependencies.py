"""
FastAPI Dependencies.

Provides injectable dependencies for:
  - Database sessions     (get_db)
  - Redis client          (get_redis)
  - Current user          (get_current_user)
  - Optional current user (get_optional_user)
"""
import uuid
from typing import Annotated, AsyncGenerator

import redis.asyncio as aioredis
from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import async_session
from app.models.user import User
from app.utils.jwt import get_subject

# ── Database Session ──────────────────────────────────────────────────────────

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session, closing it after the request."""
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


DBDep = Annotated[AsyncSession, Depends(get_db)]

# ── Redis Client ──────────────────────────────────────────────────────────────

_redis_pool: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    """Return the shared Redis connection pool (lazy initialised)."""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_pool


RedisDep = Annotated[aioredis.Redis, Depends(get_redis)]

# ── Auth: Bearer token extractor ──────────────────────────────────────────────

_bearer = HTTPBearer(auto_error=False)


async def _get_user_from_token(
    token: str,
    db: AsyncSession,
) -> User:
    """Shared helper — decode token, look up user, enforce active flag."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_id_str = get_subject(token, expected_type="access")
        user_id = uuid.UUID(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise credentials_exception

    return user


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    db: DBDep,
) -> User:
    """Require a valid Bearer access token. Raises 401 if missing or invalid."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await _get_user_from_token(credentials.credentials, db)


async def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    db: DBDep,
) -> User | None:
    """Attempt to extract the current user; return None if unauthenticated.

    Used on endpoints that work for both authenticated and anonymous users
    (e.g., POST /api/urls/shorten).
    """
    if credentials is None:
        return None
    try:
        return await _get_user_from_token(credentials.credentials, db)
    except HTTPException:
        return None


CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_user)]
