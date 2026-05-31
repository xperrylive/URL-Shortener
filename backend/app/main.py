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
from app.database import async_session, engine
from app.routers import auth, urls, redirect as redirect_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Run startup checks, then yield (app runs), then cleanup on shutdown."""
    # ── Startup ───────────────────────────────────────────────────
    # Verify database connectivity
    async with async_session() as session:
        await session.execute(text("SELECT 1"))

    # Verify Redis connectivity
    r = aioredis.from_url(settings.redis_url, decode_responses=True)
    await r.ping()
    await r.aclose()

    yield  # Application is now running

    # ── Shutdown ──────────────────────────────────────────────────
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

    # ── Routers ───────────────────────────────────────────────────
    app.include_router(auth.router)
    app.include_router(urls.router)
    # Redirect router is included LAST — its /{short_code} catch-all
    # must not shadow any /api/* routes above it.
    app.include_router(redirect_router.router)

    # ── Health Check ──────────────────────────────────────────────
    @app.get("/health", tags=["Health"], summary="Service health check")
    async def health() -> dict:
        return {"status": "ok", "environment": settings.environment}

    return app


app = create_app()
