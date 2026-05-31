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

**Phase:** Setup Complete — Ready for Day 1 MVP Build

**Last Action:** Scaffolded full backend directory structure + committed to Git.

**Next Step:** Begin Day 1 MVP Backend implementation (see checklist below).

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
- [ ] **Step 4:** Set up `requirements.txt` with all dependencies
- [ ] **Step 5:** Write `app/config.py` (pydantic-settings, .env loading)
- [ ] **Step 6:** Write `app/database.py` (async SQLAlchemy engine + session factory)
- [ ] **Step 7:** Write SQLAlchemy models (`models/user.py`, `models/url.py`, `models/click.py`)
- [ ] **Step 8:** Initialize Alembic + write first migration
- [ ] **Step 9:** Write Pydantic schemas (`schemas/auth.py`, `schemas/url.py`, `schemas/analytics.py`)
- [ ] **Step 10:** Write JWT utilities (`utils/jwt.py`)
- [ ] **Step 11:** Write `dependencies.py` (`get_db`, `get_current_user`, `get_redis`)
- [ ] **Step 12:** Implement auth router (`routers/auth.py`) — register, login, refresh, logout
- [ ] **Step 13:** Implement URL shortener service (`services/shortener.py`) + URL router (`routers/urls.py`)
- [ ] **Step 14:** Implement redirect router (`routers/redirect.py`) with Redis cache
- [ ] **Step 15:** Implement click counter (synchronous increment for MVP)
- [ ] **Step 16:** Implement list URLs endpoint
- [ ] **Step 17:** Write `app/main.py` (app factory, router registration, CORS)
- [ ] **Step 18:** Write `Dockerfile` + `docker-compose.yml`
- [ ] **Step 19:** Write `.env.example`
- [ ] **Step 20:** Write smoke tests (`tests/test_auth.py`, `tests/test_urls.py`, `tests/test_redirect.py`)

### Frontend (After Backend MVP)
- [ ] Landing page with URL input
- [ ] Register + Login pages
- [ ] Dashboard URL table with copy button
- [ ] Connect to live backend API
- [ ] Deploy to Vercel

---

## Post-MVP Roadmap (do not build yet)

1. Custom aliases
2. Async click logging (BackgroundTasks)
3. GeoIP analytics
4. Redis rate limiting
5. Link expiration (TTL)
6. Analytics dashboard (charts)
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
| (pending) | `chore: initialize git repository` |
| (pending) | `chore: add project scratchpad (antigravity.md)` |
| (pending) | `feat: scaffold backend directory structure` |
