"""
FastAPI Application Factory.

- CORS configured for frontend origin(s)
- All routers registered
- Health check endpoint
- Lifespan context: verify DB + Redis connectivity on startup
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.database import Base, async_session, engine
from app.routers import auth, urls, redirect as redirect_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Run startup checks, then yield (app runs), then cleanup on shutdown."""
    # ── Startup ───────────────────────────────────────────────────
    # Auto-create tables for SQLite in development environment
    if settings.environment.lower() == "development" and "sqlite" in settings.database_url:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    # Verify database connectivity
    async with async_session() as session:
        await session.execute(text("SELECT 1"))

    # Verify Redis connectivity (using get_redis wrapper)
    from app.dependencies import get_redis
    r = await get_redis()
    await r.ping()

    yield  # Application is now running

    # ── Shutdown ──────────────────────────────────────────────────
    # Clean up DB connections
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="URL Shortener API",
        description=(
            "A production-ready URL shortener with analytics. "
            "Built with FastAPI, async SQLAlchemy, PostgreSQL, and Redis."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,   # needed for httpOnly cookie
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Health Check ──────────────────────────────────────────────
    @app.get("/health", tags=["Health"], summary="Service health check")
    async def health() -> dict:
        return {"status": "ok", "environment": settings.environment}

    # ── Routers ───────────────────────────────────────────────────
    app.include_router(auth.router)
    app.include_router(urls.router)
    # Redirect router is included LAST — its /{short_code} catch-all
    # must not shadow any /api/* routes above it.
    app.include_router(redirect_router.router)

    return app


app = create_app()
