"""
Auth Router.

POST   /api/auth/register  → Register a new user
POST   /api/auth/login     → Login, return access token + set httpOnly refresh cookie
POST   /api/auth/refresh   → Issue new access token from refresh cookie
DELETE /api/auth/logout    → Clear refresh cookie (requires valid access token)
"""
import uuid

import bcrypt
from fastapi import APIRouter, Cookie, HTTPException, Response, status
from sqlalchemy import select

from app.config import settings
from app.dependencies import CurrentUser, DBDep
from app.models.user import User
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.utils.jwt import create_access_token, create_refresh_token, get_subject

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# ── Password hashing (direct bcrypt — compatible with bcrypt 5.x / Python 3.13) ──

def hash_password(plain: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ── Cookie helper ─────────────────────────────────────────────────────────────

def _set_refresh_cookie(response: Response, token: str) -> None:
    """Write the refresh token into an httpOnly cookie."""
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        secure=settings.is_production,   # HTTPS-only in production
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 86400,
        path="/api/auth",                # scope to auth routes only
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(body: RegisterRequest, response: Response, db: DBDep) -> AuthResponse:
    """Create a new user, return access token, set refresh cookie."""
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = User(email=body.email, password_hash=hash_password(body.password), tier="free")
    db.add(user)
    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(str(user.id))
    _set_refresh_cookie(response, create_refresh_token(str(user.id)))

    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login and receive tokens",
)
async def login(body: LoginRequest, response: Response, db: DBDep) -> AuthResponse:
    """Validate credentials, return access token, set refresh cookie."""
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated.")

    access_token = create_access_token(str(user.id))
    _set_refresh_cookie(response, create_refresh_token(str(user.id)))

    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token using refresh cookie",
)
async def refresh(
    response: Response,
    db: DBDep,
    refresh_token: str | None = Cookie(default=None),
) -> TokenResponse:
    """Issue a new access token (and rotate refresh token) from the httpOnly cookie."""
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing.")

    try:
        user_id_str = get_subject(refresh_token, expected_type="refresh")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        )

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id_str)))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")

    new_access = create_access_token(str(user.id))
    _set_refresh_cookie(response, create_refresh_token(str(user.id)))  # rotate refresh token

    return TokenResponse(
        access_token=new_access,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.delete(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout — clears refresh token cookie",
)
async def logout(response: Response, _: CurrentUser) -> None:
    """Requires a valid access token; clears the refresh cookie."""
    response.delete_cookie(key="refresh_token", path="/api/auth")
