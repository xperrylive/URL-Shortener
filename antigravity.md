# Antigravity — URL Shortener Project Scratchpad

> Internal context tracker. Updated after every major step. Do not delete.

---

## Project Overview

- **App:** URL Shortener with Analytics
- **Backend:** FastAPI + SQLAlchemy 2.0 (async) + PostgreSQL + Redis
- **Frontend:** Next.js 14 (App Router) + Tailwind + shadcn/ui
- **Auth:** JWT (access + refresh tokens) via python-jose + passlib/bcrypt
- **Hosting:** Railway (backend) + Supabase (DB) + Redis Cloud + Vercel (frontend)
- **PRD Source:** `url-shortener-app-details.md`

---

## Current Status

**Phase:** Deployment Preparation — IN PROGRESS 🚀

**Last Action:** Prepared CI/CD pipeline (GitHub Actions), production Dockerfile (multi-stage), railway.json, vercel.json, and updated env examples.

**Next Step:** Push to GitHub, set repo secrets, trigger first deployment to Railway + Vercel.

---

## Session Context

- Working directory: `c:\Users\saadm\Desktop\Programming\URL shortener`
- Backend root: `backend/`
- Frontend root: `frontend/` (not started yet)
- Git: initialized ✅

---

## MVP Checklist — Day 1 Build

### Backend (Priority Order)
- [x] Initialize Git repository
- [x] Create `antigravity.md` scratchpad
- [x] Scaffold backend directory structure
- [x] **Step 4:** Set up `requirements.txt` with all dependencies
- [x] **Step 5:** `app/config.py` — pydantic-settings, .env loading, CORS helper
- [x] **Step 6:** `app/database.py` — async SQLAlchemy engine + session factory, DeclarativeBase
- [x] **Step 7:** SQLAlchemy models (`models/user.py`, `models/url.py`, `models/click.py`)
- [x] **Step 8:** Alembic initialized (`alembic.ini`, `alembic/env.py`, `alembic/script.py.mako`)
- [x] **Step 9:** Pydantic schemas (`schemas/auth.py`, `schemas/url.py`, `schemas/analytics.py`)
- [x] **Step 10:** JWT utilities (`utils/jwt.py`) + device parser (`utils/device_parser.py`)
- [x] **Step 11:** `dependencies.py` — get_db, get_current_user, get_optional_user, get_redis
- [x] **Step 12:** Auth router — register, login, refresh (cookie), logout
- [x] **Step 13:** Shortener service (base62, collision check, alias validation) + URL router (CRUD)
- [x] **Step 14:** Redirect router — Redis-first, negative caching, 410 for expired
- [x] **Step 15:** Click counter — BackgroundTask (async increment via `update(URL)`)
- [x] **Step 16:** List URLs endpoint — paginated, owner-scoped
- [x] **Step 17:** `app/main.py` — lifespan startup checks, CORS, ordered router registration
- [x] **Step 18:** `Dockerfile` + `docker-compose.yml` (FastAPI + Postgres 16 + Redis 7)
- [x] **Step 19:** `.env.example` with all required env vars
- [x] **Step 20:** Tests — `conftest.py` (SQLite + fakeredis), `test_auth.py`, `test_urls.py`, `test_redirect.py`

### Frontend (Priority Order)
- [x] Landing page with URL input → show shortened result
- [x] Register + Login pages
- [x] Dashboard URL table with copy button and click counts
- [x] Connect all pages to live backend API
- [ ] Deploy to Vercel

### Deployment
- [x] Production Dockerfile (multi-stage, non-root user)
- [x] `railway.json` — Railway service config (auto-runs `alembic upgrade head` on deploy)
- [x] `vercel.json` — Vercel project config
- [x] GitHub Actions CI (`.github/workflows/ci.yml`) — pytest + Next.js build on every PR
- [x] GitHub Actions CD (`.github/workflows/cd.yml`) — auto-deploy to Railway + Vercel on `main` merge
- [ ] Push repo to GitHub
- [ ] Set GitHub repo secrets (RAILWAY_TOKEN, VERCEL_TOKEN, etc.)
- [ ] Set environment variables in Railway service
- [ ] Set environment variables in Vercel project
- [ ] Trigger first deploy & verify `/health` endpoint
- [ ] Run `alembic upgrade head` against production DB (auto-runs via railway.json)

---

## Post-MVP Roadmap (do not build yet)

1. [x] Custom aliases
2. [x] Async click logging (BackgroundTasks)
3. [ ] GeoIP analytics
4. [x] Redis rate limiting
5. [x] Link expiration (TTL)
6. [ ] Analytics dashboard (charts)
7. QR code generation
8. API key auth
9. Celery Beat nightly cleanup
10. GraphQL (Strawberry)
11. Prometheus + Grafana

---

## Architecture Notes

### Short Code Generation
- 6-char base62 (alphanumeric) from hash(url + timestamp + salt)
- Collision retry: up to 3 attempts
- Custom alias: 3–30 chars, alphanumeric + hyphens, no reserved words

### Redirect Flow (Redis-first)
1. Check Redis `url:{short_code}`
2. Cache miss → query Postgres
3. 404 if not found / inactive; 410 if expired
4. Cache with TTL=3600s
5. 301 redirect
6. Background task: log click

### Auth Tokens
- Access: JWT, 30-min expiry, in Authorization header
- Refresh: JWT, 7-day expiry, in httpOnly cookie

### Rate Limits (post-MVP)
- Anonymous: 10 shortens/day/IP
- Free tier: 50 shortens/day
- Pro: unlimited

---

## Key File Map

| File | Purpose |
|---|---|
| `backend/app/main.py` | App factory, CORS, router registration |
| `backend/app/config.py` | pydantic-settings, .env loader |
| `backend/app/database.py` | Async engine, session factory |
| `backend/app/dependencies.py` | get_db, get_current_user, get_redis |
| `backend/app/models/user.py` | User ORM model |
| `backend/app/models/url.py` | URL ORM model |
| `backend/app/models/click.py` | Click ORM model |
| `backend/app/schemas/auth.py` | Register/Login Pydantic schemas |
| `backend/app/schemas/url.py` | Shorten/URL response schemas |
| `backend/app/schemas/analytics.py` | Analytics response schemas |
| `backend/app/routers/auth.py` | Auth endpoints |
| `backend/app/routers/urls.py` | URL CRUD endpoints |
| `backend/app/routers/redirect.py` | GET /{short_code} redirect |
| `backend/app/routers/analytics.py` | Analytics endpoints |
| `backend/app/routers/qr.py` | QR code endpoint |
| `backend/app/services/shortener.py` | base62, collision check |
| `backend/app/services/cache.py` | Redis wrappers |
| `backend/app/services/analytics.py` | Aggregation queries |
| `backend/app/services/geo.py` | GeoIP resolution |
| `backend/app/tasks/click_logger.py` | Background click logging |
| `backend/app/utils/jwt.py` | Token create/verify |
| `backend/app/utils/rate_limiter.py` | Redis sliding window |
| `backend/app/utils/device_parser.py` | UA → device type |
| `backend/alembic/` | DB migrations |
| `backend/tests/` | pytest test suite |

---

## Git Log Summary

| Commit | Message |
|---|---|
| 8303962 | `chore: initialize git repository with gitignore and README` |
| 1223281 | `feat: scaffold backend directory structure per PRD section 9` |
| 1dc11fc | `feat: implement config (pydantic-settings) and async database engine` |
| 4d77ba9 | `feat: implement SQLAlchemy ORM models (User, URL, Click)` |
| 83863d4 | `feat: implement Pydantic schemas, JWT utils, device parser, and Alembic migration setup` |
| 090c511 | `feat: implement auth router, URL router, redirect router, and core services` |
| d7539ac | `feat: add SQLite and InMemoryRedis fallback for local non-Docker development` |
| 14d5999 | `feat: complete frontend MVP, implement rate limiting, and add custom 404 redirect handling` |
| pending | `chore: prepare deployment — CI/CD pipeline, production Dockerfile, railway + vercel config` |
