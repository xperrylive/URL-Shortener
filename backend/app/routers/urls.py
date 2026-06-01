"""
URLs Router.

POST   /api/urls/shorten           → Create a short URL (auth optional)
GET    /api/urls/                  → List authenticated user's URLs (paginated)
GET    /api/urls/{short_code}      → Get URL details (owner only)
PATCH  /api/urls/{short_code}      → Update alias or expiry (owner only)
DELETE /api/urls/{short_code}      → Deactivate a URL (owner only)
"""
import math
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, Request, status
from sqlalchemy import func, select

from app.dependencies import CurrentUser, DBDep, OptionalUser, RedisDep
from app.models.url import URL
from app.schemas.url import ShortenRequest, URLListResponse, URLResponse, UpdateURLRequest
from app.services.cache import invalidate_url_cache
from app.services.shortener import build_short_url, generate_short_code, validate_custom_alias
from app.utils.rate_limiter import check_rate_limit

router = APIRouter(prefix="/api/urls", tags=["URLs"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _to_response(url: URL) -> URLResponse:
    return URLResponse(
        id=url.id,
        original_url=url.original_url,
        short_code=url.short_code,
        short_url=build_short_url(url.short_code),
        custom_alias=url.custom_alias,
        user_id=url.user_id,
        is_active=url.is_active,
        expires_at=url.expires_at,
        click_count=url.click_count,
        created_at=url.created_at,
        updated_at=url.updated_at,
    )


async def _get_owned_url(short_code: str, user_id: uuid.UUID, db) -> URL:
    """Fetch a URL by short_code and enforce ownership. Raises 404/403."""
    result = await db.execute(select(URL).where(URL.short_code == short_code))
    url = result.scalar_one_or_none()
    if url is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found.")
    if url.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised.")
    return url


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "/shorten",
    response_model=URLResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Shorten a URL (authentication optional)",
)
async def shorten_url(
    body: ShortenRequest,
    request: Request,
    db: DBDep,
    redis: RedisDep,
    current_user: OptionalUser,
) -> URLResponse:
    """Create a short URL. Anonymous users may create links; authenticated users own them."""
    
    # Rate Limiting
    if current_user is None:
        client_ip = request.client.host if request.client else "unknown"
        await check_rate_limit(redis, identifier=client_ip, is_anonymous=True)
    elif current_user.tier != "pro":
        await check_rate_limit(redis, identifier=str(current_user.id), is_anonymous=False)

    original_url = str(body.url)

    # Validate custom alias if provided
    if body.custom_alias:
        try:
            validate_custom_alias(body.custom_alias)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

        # Check alias uniqueness
        alias_check = await db.execute(
            select(URL.id).where(URL.custom_alias == body.custom_alias)
        )
        if alias_check.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Custom alias '{body.custom_alias}' is already taken.",
            )
        short_code = body.custom_alias
    else:
        short_code = await generate_short_code(db, original_url)

    url = URL(
        original_url=original_url,
        short_code=short_code,
        custom_alias=body.custom_alias,
        user_id=current_user.id if current_user else None,
        expires_at=body.expires_at,
    )
    db.add(url)
    await db.commit()
    await db.refresh(url)

    return _to_response(url)


@router.get(
    "/",
    response_model=URLListResponse,
    summary="List authenticated user's shortened URLs",
)
async def list_urls(
    db: DBDep,
    current_user: CurrentUser,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
) -> URLListResponse:
    offset = (page - 1) * page_size

    # Total count
    count_result = await db.execute(
        select(func.count(URL.id)).where(URL.user_id == current_user.id)
    )
    total = count_result.scalar_one()

    # Active count
    active_result = await db.execute(
        select(func.count(URL.id)).where(URL.user_id == current_user.id, URL.is_active == True)
    )
    total_active = active_result.scalar_one()

    # Total clicks
    clicks_result = await db.execute(
        select(func.sum(URL.click_count)).where(URL.user_id == current_user.id)
    )
    total_clicks = clicks_result.scalar_one() or 0

    # Paginated items
    items_result = await db.execute(
        select(URL)
        .where(URL.user_id == current_user.id)
        .order_by(URL.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    urls = items_result.scalars().all()

    return URLListResponse(
        items=[_to_response(u) for u in urls],
        total=total,
        total_active=total_active,
        total_clicks=total_clicks,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total > 0 else 1,
    )


@router.get(
    "/{short_code}",
    response_model=URLResponse,
    summary="Get URL details (owner only)",
)
async def get_url(short_code: str, db: DBDep, current_user: CurrentUser) -> URLResponse:
    url = await _get_owned_url(short_code, current_user.id, db)
    return _to_response(url)


@router.patch(
    "/{short_code}",
    response_model=URLResponse,
    summary="Update a URL's alias, expiry, or active status",
)
async def update_url(
    short_code: str,
    body: UpdateURLRequest,
    db: DBDep,
    redis: RedisDep,
    current_user: CurrentUser,
) -> URLResponse:
    url = await _get_owned_url(short_code, current_user.id, db)

    if body.custom_alias is not None:
        try:
            validate_custom_alias(body.custom_alias)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
        # Uniqueness check (exclude self)
        alias_check = await db.execute(
            select(URL.id).where(URL.custom_alias == body.custom_alias, URL.id != url.id)
        )
        if alias_check.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Custom alias '{body.custom_alias}' is already taken.",
            )
        url.custom_alias = body.custom_alias

    if body.expires_at is not None:
        url.expires_at = body.expires_at

    if body.is_active is not None:
        url.is_active = body.is_active

    url.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(url)

    # Invalidate cache so the redirect picks up the new state
    await invalidate_url_cache(redis, short_code)

    return _to_response(url)


@router.delete(
    "/{short_code}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate (soft-delete) a URL",
)
async def delete_url(
    short_code: str,
    db: DBDep,
    redis: RedisDep,
    current_user: CurrentUser,
) -> None:
    url = await _get_owned_url(short_code, current_user.id, db)
    url.is_active = False
    url.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await invalidate_url_cache(redis, short_code)
