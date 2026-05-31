# URL Shortener with Analytics

A production-ready URL shortening API built with FastAPI, async SQLAlchemy, PostgreSQL, and Redis.

## Tech Stack

- **Framework:** FastAPI (async)
- **ORM:** SQLAlchemy 2.0 (async mode)
- **Database:** PostgreSQL 16 (Supabase in production)
- **Cache:** Redis 7 (Redis Cloud in production)
- **Auth:** JWT (python-jose) + bcrypt (passlib)
- **Hosting:** Railway (API) + Supabase (DB) + Redis Cloud + Vercel (Frontend)

## Local Development

### Prerequisites
- Docker + Docker Compose
- Python 3.11+

### Quick Start

```bash
cd backend

# 1. Copy env template
cp .env.example .env
# Edit .env — fill in SECRET_KEY at minimum for local dev

# 2. Start services (FastAPI + Postgres + Redis)
docker-compose up --build

# 3. Run migrations (once DB is up)
docker-compose exec api alembic upgrade head
```

API will be available at `http://localhost:8000`  
Swagger docs at `http://localhost:8000/docs`

### GeoIP Database

Download the free MaxMind GeoLite2-City database:
1. Sign up at https://www.maxmind.com/en/geolite2/signup
2. Download `GeoLite2-City.mmdb`
3. Place it at the path specified in `GEOIP_DB_PATH` (default: `/app/GeoLite2-City.mmdb`)

### Running Tests

```bash
docker-compose exec api pytest tests/ -v --cov=app
```

## API Documentation

| Router | Base Path | Description |
|---|---|---|
| Auth | `/api/auth` | Register, login, refresh, logout |
| URLs | `/api/urls` | Shorten, list, update, delete |
| Redirect | `/` | Short code → original URL redirect |
| Analytics | `/api/analytics` | Click stats, time-series, geo, device |
| QR Codes | `/api/qr` | QR code image generation |

Full interactive docs: `http://localhost:8000/docs`

## Project Structure

```
backend/
├── app/
│   ├── main.py           ← FastAPI app factory, CORS, router registration
│   ├── config.py         ← pydantic-settings (.env loader)
│   ├── database.py       ← Async SQLAlchemy engine + session
│   ├── dependencies.py   ← get_db, get_current_user, get_redis
│   ├── models/           ← SQLAlchemy ORM models (User, URL, Click)
│   ├── schemas/          ← Pydantic v2 request/response schemas
│   ├── routers/          ← FastAPI routers (auth, urls, redirect, analytics, qr)
│   ├── services/         ← Business logic (shortener, cache, analytics, geo)
│   ├── tasks/            ← Background tasks (click logging)
│   └── utils/            ← JWT, rate limiter, device parser
├── alembic/              ← Database migrations
├── tests/                ← pytest test suite
├── .env.example          ← Environment variable template
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```
