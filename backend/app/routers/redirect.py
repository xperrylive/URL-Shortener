"""
Redirect Router.

GET /{short_code}
  1. Check Redis cache (url:{short_code})
  2. Cache miss → query Postgres
  3. 404 if not found or inactive; 410 if expired
  4. Cache result with TTL=3600s
  5. 301 redirect to original URL
  6. Fire BackgroundTask to increment click_count (MVP: synchronous DB update)
"""
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select, update

from app.database import async_session
from app.dependencies import DBDep, RedisDep
from app.models.url import URL
from app.services.cache import (
    get_cached_url,
    is_inactive_sentinel,
    set_cached_url,
    set_inactive_cache,
)

router = APIRouter(tags=["Redirect"])


# ── Background Task ───────────────────────────────────────────────────────────

async def _log_click(short_code: str, session_factory=None) -> None:
    """Increment click_count for the given short_code.

    Accepts an optional session_factory override so tests can substitute
    the SQLite test engine instead of the real PostgreSQL engine.
    """
    from app.database import async_session as default_factory
    factory = session_factory or default_factory
    async with factory() as session:
        await session.execute(
            update(URL)
            .where(URL.short_code == short_code)
            .values(click_count=URL.click_count + 1)
        )
        await session.commit()


# ── Endpoint ──────────────────────────────────────────────────────────────────

@router.get(
    "/{short_code}",
    summary="Redirect to the original URL",
    response_class=RedirectResponse,
    status_code=status.HTTP_301_MOVED_PERMANENTLY,
    responses={
        301: {"description": "Redirect to original URL"},
        404: {"description": "Short code not found or link inactive"},
        410: {"description": "Link has expired"},
    },
)
async def redirect(
    short_code: str,
    request: Request,
    db: DBDep,
    redis: RedisDep,
    background_tasks: BackgroundTasks,
) -> RedirectResponse:
    # ── 1. Redis cache lookup ──────────────────────────────────────
    cached = await get_cached_url(redis, short_code)

    if cached is not None:
        if is_inactive_sentinel(cached):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found.")
        background_tasks.add_task(_log_click, short_code)
        return RedirectResponse(url=cached, status_code=status.HTTP_301_MOVED_PERMANENTLY)

    # ── 2. DB lookup (cache miss) ──────────────────────────────────
    result = await db.execute(select(URL).where(URL.short_code == short_code))
    url_obj = result.scalar_one_or_none()

    if url_obj is None:
        await set_inactive_cache(redis, short_code)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found.")

    if not url_obj.is_active:
        await set_inactive_cache(redis, short_code)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This link is no longer active.",
        )

    if url_obj.expires_at is not None:
        # Handle both timezone-aware (PostgreSQL) and naive (SQLite in tests) datetimes
        expires = url_obj.expires_at
        now = datetime.now(timezone.utc)
        if expires.tzinfo is None:
            # SQLite returns naive datetimes — treat stored value as UTC
            from datetime import timezone as _tz
            expires = expires.replace(tzinfo=_tz.utc)
        if expires < now:
            await set_inactive_cache(redis, short_code)
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="This link has expired.",
            )

    # ── 3. Populate cache & redirect ───────────────────────────────
    await set_cached_url(redis, short_code, url_obj.original_url)
    background_tasks.add_task(_log_click, short_code)
    return RedirectResponse(url=url_obj.original_url, status_code=status.HTTP_301_MOVED_PERMANENTLY)
