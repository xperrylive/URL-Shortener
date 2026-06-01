# URL Shortener with Analytics — Full Application Details
> Feed this document to an LLM to generate a complete, detailed PRD.

---

## 1. Project Overview

A full-stack URL shortening web application with real-time analytics, QR code generation, and a clean modern dashboard. The project is built as a portfolio piece targeting backend internship applications, demonstrating skills in async Python APIs, relational database design, caching, background task processing, and modern frontend development.

**Target Users:** Developers, marketers, and general users who want to shorten URLs and track their performance.

**Business Goals:**
- Allow users to shorten long URLs into short, shareable links
- Track click analytics per link (geography, device, referrer, time)
- Provide a dashboard to manage and visualize link performance
- Support link customization, expiration, and QR code generation

---

## 2. Tech Stack

### Backend
| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Framework | FastAPI (async-native) |
| ORM | SQLAlchemy 2.0 (async mode) |
| Database Driver | asyncpg |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Authentication | JWT via python-jose + passlib (bcrypt) |
| Background Tasks | FastAPI BackgroundTasks (MVP), Celery Beat (later for scheduled jobs) |
| Caching | Redis (via aioredis) |
| GeoIP | geoip2 + MaxMind GeoLite2 database |
| QR Codes | qrcode[pil] library |
| API Docs | Built-in Swagger UI + ReDoc (FastAPI default) |
| Testing | pytest + pytest-asyncio + httpx |
| Containerization | Docker + Docker Compose |

### Frontend
| Layer | Technology |
|---|---|
| Framework | Next.js 14 (App Router) |
| Styling | Tailwind CSS |
| UI Components | shadcn/ui |
| Charts | Recharts |
| QR Display | react-qr-code |
| State Management | Zustand |
| HTTP Client | Axios |
| Hosting | Vercel |

### Infrastructure & Hosting
| Service | Platform | Tier |
|---|---|---|
| Backend API | Railway | Free |
| PostgreSQL Database | Supabase | Free (500MB) |
| Redis Cache | Redis Cloud | Free (30MB) |
| Frontend | Vercel | Free |

---

## 3. Database Schema

### Table: `users`
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PRIMARY KEY, default gen_random_uuid() |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| api_key | VARCHAR(64) | UNIQUE, nullable |
| tier | ENUM('free', 'pro') | DEFAULT 'free' |
| is_active | BOOLEAN | DEFAULT true |
| created_at | TIMESTAMP | DEFAULT now() |
| updated_at | TIMESTAMP | DEFAULT now() |

### Table: `urls`
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PRIMARY KEY |
| original_url | TEXT | NOT NULL |
| short_code | VARCHAR(20) | UNIQUE, NOT NULL, INDEXED |
| custom_alias | VARCHAR(50) | UNIQUE, nullable |
| user_id | UUID | FK → users.id, nullable (anonymous) |
| is_active | BOOLEAN | DEFAULT true |
| expires_at | TIMESTAMP | nullable |
| click_count | INTEGER | DEFAULT 0 |
| created_at | TIMESTAMP | DEFAULT now() |
| updated_at | TIMESTAMP | DEFAULT now() |

### Table: `clicks`
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PRIMARY KEY |
| url_id | UUID | FK → urls.id, INDEXED |
| ip_address | VARCHAR(45) | nullable |
| country | VARCHAR(100) | nullable |
| city | VARCHAR(100) | nullable |
| referrer | TEXT | nullable |
| user_agent | TEXT | nullable |
| device_type | ENUM('mobile', 'desktop', 'bot', 'unknown') | DEFAULT 'unknown' |
| clicked_at | TIMESTAMP | DEFAULT now(), INDEXED |

**Indexes:**
- `urls.short_code` — for fast redirect lookups
- `clicks.url_id` — for analytics queries
- `clicks.clicked_at` — for time-series analytics

---

## 4. API Endpoints

### Authentication — `/api/auth`

| Method | Path | Description | Auth Required |
|---|---|---|---|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login, returns access + refresh token | No |
| POST | `/api/auth/refresh` | Refresh access token | No (refresh token) |
| DELETE | `/api/auth/logout` | Invalidate refresh token | Yes |

### URLs — `/api/urls`

| Method | Path | Description | Auth Required |
|---|---|---|---|
| POST | `/api/urls/shorten` | Create a short URL | Optional |
| GET | `/api/urls/` | List authenticated user's URLs (paginated) | Yes |
| GET | `/api/urls/{short_code}` | Get URL details | Yes (owner) |
| PATCH | `/api/urls/{short_code}` | Update alias or expiry | Yes (owner) |
| DELETE | `/api/urls/{short_code}` | Deactivate a URL | Yes (owner) |

### Redirect — Root level

| Method | Path | Description | Auth Required |
|---|---|---|---|
| GET | `/{short_code}` | Redirect to original URL, log click | No |

### Analytics — `/api/analytics`

| Method | Path | Description | Auth Required |
|---|---|---|---|
| GET | `/api/analytics/{short_code}/summary` | Total clicks, unique countries, top device | Yes (owner) |
| GET | `/api/analytics/{short_code}/clicks` | Paginated click history | Yes (owner) |
| GET | `/api/analytics/{short_code}/time-series` | Clicks per day (last 7 or 30 days) | Yes (owner) |
| GET | `/api/analytics/{short_code}/countries` | Click breakdown by country | Yes (owner) |
| GET | `/api/analytics/{short_code}/devices` | Click breakdown by device type | Yes (owner) |
| GET | `/api/analytics/{short_code}/referrers` | Top referrers | Yes (owner) |
| GET | `/api/analytics/dashboard` | Aggregate stats across all user URLs | Yes |

### QR Codes — `/api/qr`

| Method | Path | Description | Auth Required |
|---|---|---|---|
| GET | `/api/qr/{short_code}` | Return QR code as PNG image | Yes (owner) |

---

## 5. Core Business Logic

### Short Code Generation
- Default: 6-character alphanumeric code using base62 encoding of a hash of (original_url + timestamp + random salt)
- Collision check: query DB before saving; regenerate on collision (max 3 retries)
- Custom alias: user-provided, validated as 3–30 chars, alphanumeric + hyphens only, no reserved words (e.g. "api", "dashboard", "admin")
- Short codes are case-sensitive

### Redirect Flow
1. Request hits `GET /{short_code}`
2. Check Redis cache for key `url:{short_code}` → if hit, get original URL
3. If cache miss → query Postgres `urls` table by `short_code`
4. If not found or `is_active = false` → return 404
5. If `expires_at` is set and past → return 410 Gone
6. Cache the result in Redis with TTL of 3600 seconds
7. Issue 301 redirect to original URL
8. **Fire FastAPI BackgroundTask** to log the click asynchronously (non-blocking)

### Click Logging (Background Task)
1. Receive: `url_id`, `ip_address`, `user_agent`, `referrer` from request
2. Parse `user_agent` string to detect: `mobile`, `desktop`, `bot`
3. Resolve `ip_address` → `country`, `city` using geoip2 + MaxMind GeoLite2
4. Insert row into `clicks` table
5. Increment `urls.click_count` counter

### Rate Limiting (Redis sliding window)
- Key format: `ratelimit:shorten:{ip}` or `ratelimit:shorten:{user_id}`
- Anonymous users: 10 shortens per day per IP
- Authenticated free tier: 50 shortens per day
- Pro tier: unlimited
- Return HTTP 429 with `Retry-After` header when exceeded

### Link Expiration
- `expires_at` field stored on `urls` table (nullable)
- Checked on every redirect request
- Expired links return HTTP 410 Gone
- (Future) Celery Beat job runs nightly to set `is_active = false` on all expired URLs

### QR Code Generation
- Generated server-side using `qrcode[pil]` Python library
- Target URL is the full short URL (e.g. `https://yourdomain.com/{short_code}`)
- Returned as PNG image bytes with `Content-Type: image/png`
- (Future) Cache generated QR codes in Redis or object storage

---

## 6. Authentication & Security

- **Password hashing:** bcrypt via passlib
- **Access token:** JWT, 30-minute expiry
- **Refresh token:** JWT, 7-day expiry, stored in httpOnly cookie
- **API key auth (future):** Static key in `Authorization: Bearer <api_key>` header, stored hashed in DB
- **CORS:** Configured to allow only the frontend Vercel domain in production
- **Input validation:** All inputs validated via Pydantic v2 schemas, rejecting malformed URLs and oversized payloads
- **SQL injection:** Fully prevented by SQLAlchemy ORM parameterized queries

---

## 7. Frontend Pages & Components

### Page: Landing `/`
- Full-width hero with app name, tagline, and a prominent URL input box
- User pastes a long URL and clicks "Shorten"
- Returns the short URL immediately with a copy button
- For anonymous users: shows the result inline, prompts to sign up for analytics
- Design: dark background, single accent color (purple or blue), Inter font, minimal nav

### Page: Register `/register`
- Email + password fields
- Password strength indicator
- Redirects to dashboard on success

### Page: Login `/login`
- Email + password
- "Remember me" checkbox
- Link to register

### Page: Dashboard `/dashboard`
- Top summary strip: total URLs created, total clicks all-time, top performing URL
- Table of all user's shortened URLs
  - Columns: Short URL (with copy button), Original URL (truncated), Clicks, Created date, Status (active/expired), Actions
  - Actions: View Analytics, Show QR, Edit, Delete
- Pagination (10 per page)
- Search/filter bar to find URLs by original URL or short code

### Page: Analytics `/dashboard/[short_code]`
- Header: short URL, original URL, created date, expiry, status
- **Summary cards:** Total clicks, Unique countries, Top device, Top referrer
- **Line chart:** Clicks over time (toggle: last 7 days / 30 days) — using Recharts
- **Bar chart:** Top 10 countries by click count
- **Donut chart:** Device type breakdown (mobile / desktop / bot)
- **Table:** Top referrers (domain + count)
- **QR Code section:** QR image displayed, download as PNG button
- **Link settings:** Edit alias, set/change expiry date, deactivate link

### Page: Settings `/settings`
- Update email, update password
- (Future) View/regenerate API key

### Global Components
- `Navbar` — logo left, nav links, user avatar + logout right
- Dark/light mode toggle (dark by default)
- Toast notifications for copy success, errors, etc.

---

## 8. Design System

- **Theme:** Dark mode default, light mode toggle
- **Background:** `#0a0a0a` (near black)
- **Surface / Card:** `#111111` with `1px` border `#222222`
- **Accent:** Purple `#7c3aed` or Blue `#2563eb` — pick one and use consistently
- **Text primary:** `#ffffff`
- **Text secondary:** `#a1a1aa`
- **Font:** Inter (Google Fonts)
- **Border radius:** `8px` for cards, `6px` for inputs/buttons
- **Chart colors:** Accent color for primary series, muted tones for secondary
- **Animations:** Subtle fade-in on charts, smooth transitions on hover states

---

## 9. Project File Structure

### Backend
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  ← FastAPI app, router registration, CORS
│   ├── config.py                ← Settings via pydantic-settings (.env)
│   ├── database.py              ← Async SQLAlchemy engine + session
│   ├── dependencies.py          ← get_db, get_current_user, get_redis
│   ├── models/
│   │   ├── user.py
│   │   ├── url.py
│   │   └── click.py
│   ├── schemas/
│   │   ├── auth.py              ← Register/Login request + response schemas
│   │   ├── url.py               ← ShortenRequest, URLResponse, UpdateURL
│   │   └── analytics.py        ← Summary, TimeSeries, CountryStats, etc.
│   ├── routers/
│   │   ├── auth.py
│   │   ├── urls.py
│   │   ├── analytics.py
│   │   ├── qr.py
│   │   └── redirect.py          ← GET /{short_code}
│   ├── services/
│   │   ├── shortener.py         ← base62, collision check, alias validation
│   │   ├── cache.py             ← Redis get/set/delete wrappers
│   │   ├── analytics.py         ← Query aggregation logic
│   │   └── geo.py               ← IP → country/city via geoip2
│   ├── tasks/
│   │   └── click_logger.py      ← Background task: parse UA, geoip, insert click
│   └── utils/
│       ├── rate_limiter.py      ← Redis sliding window rate limiter
│       ├── jwt.py               ← Token creation + verification
│       └── device_parser.py     ← User-agent → device type
├── alembic/
│   └── versions/                ← Migration files
├── tests/
│   ├── test_auth.py
│   ├── test_urls.py
│   ├── test_redirect.py
│   └── test_analytics.py
├── .env.example
├── Dockerfile
├── docker-compose.yml           ← FastAPI + Postgres + Redis for local dev
└── requirements.txt
```

### Frontend
```
frontend/
├── app/
│   ├── page.tsx                 ← Landing page
│   ├── login/page.tsx
│   ├── register/page.tsx
│   ├── dashboard/
│   │   ├── page.tsx             ← URL table
│   │   └── [short_code]/page.tsx ← Analytics
│   └── settings/page.tsx
├── components/
│   ├── ui/                      ← shadcn/ui components
│   ├── charts/
│   │   ├── ClicksOverTime.tsx   ← Recharts LineChart
│   │   ├── CountryBar.tsx       ← Recharts BarChart
│   │   └── DeviceDonut.tsx      ← Recharts PieChart
│   ├── UrlTable.tsx
│   ├── QRModal.tsx
│   ├── SummaryCards.tsx
│   └── Navbar.tsx
├── lib/
│   ├── api.ts                   ← Axios instance + all typed API calls
│   └── auth.ts                  ← Token helpers
├── store/
│   └── authStore.ts             ← Zustand: user, token, login/logout actions
├── types/
│   └── index.ts                 ← Shared TypeScript interfaces
└── .env.local.example
```

---

## 10. Environment Variables

### Backend `.env`
```
DATABASE_URL=postgresql+asyncpg://postgres:<password>@db.<project>.supabase.co:5432/postgres
REDIS_URL=redis://default:<password>@<host>:<port>
SECRET_KEY=<random 32-byte hex>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
BASE_URL=https://your-railway-app.up.railway.app
GEOIP_DB_PATH=/app/GeoLite2-City.mmdb
ENVIRONMENT=production
```

### Frontend `.env.local`
```
NEXT_PUBLIC_API_URL=https://your-railway-app.up.railway.app
```

---

## 11. MVP Scope (Day 1 Build)

Build only these features end-to-end and get them fully working and deployed:

**Backend:**
- [ ] User registration + login (JWT, access + refresh token)
- [ ] Shorten a URL (random 6-char short code)
- [ ] Redirect via short code (with Redis cache)
- [ ] Basic click counter (increment `urls.click_count` synchronously for MVP)
- [ ] List authenticated user's URLs
- [ ] Docker Compose for local dev (FastAPI + Postgres + Redis)
- [ ] Deploy backend to Railway with Supabase DB + Redis Cloud

**Frontend:**
- [ ] Landing page with URL input → show shortened result
- [ ] Register + Login pages
- [ ] Dashboard URL table with copy button
- [ ] Connect all pages to live backend API
- [ ] Deploy frontend to Vercel

---

## 12. Post-MVP Feature Roadmap

Add features one by one — each is a concrete talking point in interviews:

| # | Feature | Skills Demonstrated |
|---|---|---|
| 1 | Custom aliases | Input validation, uniqueness constraints |
| 2 | Async click logging via BackgroundTasks | Non-blocking I/O, task queues |
| 3 | GeoIP analytics (country/city) | Third-party data enrichment |
| 4 | Redis rate limiting | Sliding window algorithm, abuse prevention |
| 5 | Link expiration (TTL) | Scheduled logic, HTTP status codes |
| 6 | Analytics dashboard (charts) | Data aggregation, visualization |
| 7 | QR code generation | Server-side image generation |
| 8 | API key authentication | Auth patterns, programmatic access |
| 9 | Celery Beat for nightly cleanup | Distributed task scheduling |
| 10 | GraphQL API (Strawberry) | Alternative API paradigm |
| 11 | Prometheus + Grafana metrics | Observability, SRE fundamentals |

---

## 13. Resume Bullet Points (After Completion)

- Built an async URL shortener API with FastAPI achieving sub-10ms redirect latency via Redis caching
- Designed a relational schema in PostgreSQL with optimized indexes supporting time-series analytics queries across millions of clicks
- Implemented non-blocking click tracking using FastAPI BackgroundTasks, decoupling analytics ingestion from the critical redirect path
- Built a Redis sliding window rate limiter enforcing per-user and per-IP request quotas
- Deployed a production full-stack application across Railway, Supabase, Redis Cloud, and Vercel using Docker and environment-based configuration
