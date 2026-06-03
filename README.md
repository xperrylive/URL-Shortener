# URL Shortener with Real-Time Analytics

A high-performance, production-ready, full-stack URL shortening service and analytics suite. Built with a modern asynchronous Python backend (**FastAPI**, **SQLAlchemy 2.0**, **PostgreSQL**, **Redis**) and a responsive, interactive frontend (**Next.js**, **Tailwind CSS**, **shadcn/ui**).

🔗 **Live Demo:** [https://url-shortener-one-blue.vercel.app/](https://url-shortener-one-blue.vercel.app/)

## 🚀 Key Features

- **High-Performance Redirects:** Sub-10ms redirect latency using a Redis-first caching strategy.
- **Asynchronous Click Analytics:** Non-blocking tracking of visitor data (GeoIP, Device, Referrer) using FastAPI `BackgroundTasks`.
- **Modern Authentication:** Secure user signup and login utilizing JWTs with access tokens in memory and refresh tokens in secure HTTP-only cookies.
- **Sliding-Window Rate Limiting:** Rate limiter implemented in Redis to prevent service abuse.
- **QR Code Generation:** Automated, on-demand QR code creation for shortened URLs.
- **Link Expiration & Custom Aliases:** Custom path alias support and absolute time-to-live (TTL) expiration rules.
- **Developer API & Webhooks:** Outward API hooks notifying external services in real time when a redirect is triggered.
- **Interactive Dashboard:** Complete dashboard for tracking links, viewing aggregate statistics, and inspecting geographic/device charts.
- **Production-Ready & Containerized:** Full Docker setup with pre-configured CI/CD workflows for automatic deployment to Railway and Vercel.

---

## 🛠️ Tech Stack

### Backend
- **Core Framework:** [FastAPI](https://fastapi.tiangolo.com/) (async-native)
- **Database ORM:** [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (Async engine + `asyncpg`)
- **Database Migrations:** [Alembic](https://alembic.sqlalchemy.org/)
- **Caching & Rate Limiting:** [Redis](https://redis.io/)
- **Authentication:** JWT (via `python-jose`) & Password Hashing (`bcrypt` via `passlib`)
- **GeoIP Resolution:** [MaxMind GeoLite2](https://dev.maxmind.com/geoip/geolite-org-free-databases)
- **Testing:** `pytest` + `pytest-asyncio` + `fakeredis`

### Frontend
- **Framework:** [Next.js](https://nextjs.org/) (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS & [shadcn/ui](https://ui.shadcn.com/)
- **Visualizations:** [Recharts](https://recharts.org/) (interactive analytics graphs)
- **State Management:** [Zustand](https://github.com/pmndrs/zustand)
- **HTTP Client:** Axios

---

## 📂 Project Structure

```
.
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── models/           # SQLAlchemy models (User, URL, Click)
│   │   ├── schemas/          # Pydantic validation schemas
│   │   ├── routers/          # API endpoint routes
│   │   ├── services/         # Business logic (shortener, cache, analytics)
│   │   ├── tasks/            # Background worker tasks (logging, webhooks)
│   │   ├── utils/            # JWT helpers, rate limits, user-agent parsing
│   │   ├── database.py       # Async SQLAlchemy session configuration
│   │   ├── dependencies.py   # FastAPI dependency injections
│   │   └── main.py           # Application entry point & configuration
│   ├── alembic/              # Database migration history
│   ├── tests/                # Unit & Integration test suite
│   ├── Dockerfile            # Production multi-stage build
│   └── docker-compose.yml    # Full local multi-container setup
│
├── frontend/                 # Next.js Application
│   ├── app/                  # Pages (Dashboard, Analytics, Auth)
│   ├── components/           # UI Elements & Recharts components
│   ├── lib/                  # API client & auth helper utilities
│   ├── store/                # Zustand stores for state management
│   └── types/                # TypeScript interface declarations
```

---

## ⚙️ Local Development Setup

### Backend Setup

#### Option A: Docker Compose (Recommended)
This spins up the FastAPI app, PostgreSQL, and Redis automatically.

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
   *Edit `.env` and set a secure `SECRET_KEY`.*
3. Launch all containers:
   ```bash
   docker-compose up --build
   ```
4. Run migrations:
   ```bash
   docker-compose exec api alembic upgrade head
   ```

#### Option B: Local Python Environment

1. Ensure Python 3.11+ is installed.
2. Install virtual environment and dependencies:
   ```bash
   cd backend
   python -m venv env
   source env/Scripts/activate # On Windows: env\Scripts\activate
   pip install -r requirements.txt
   ```
3. Set up local Postgres and Redis instances.
4. Copy `.env.example` to `.env` and configure credentials:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/urlshortener
   REDIS_URL=redis://localhost:6379/0
   ```
5. Apply migrations and start the development server:
   ```bash
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

The backend API documentation is available at:
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### GeoIP Database Setup
To enable location tracking, you need a MaxMind GeoLite2 City database:
1. Sign up for a free account at [MaxMind](https://www.maxmind.com/en/geolite2/signup).
2. Download `GeoLite2-City.mmdb`.
3. Save it to `backend/GeoLite2-City.mmdb` (or specify a custom path via `GEOIP_DB_PATH` in `.env`).

---

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Create the environment configuration:
   ```bash
   cp .env.local.example .env.local
   ```
   Ensure `NEXT_PUBLIC_API_URL` points to your backend instance:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
4. Run the development server:
   ```bash
   npm run dev
   ```
5. Open your browser and navigate to [http://localhost:3000](http://localhost:3000).

---

## 🧪 Testing

Execute the test suite using pytest:
```bash
# Using Docker
docker-compose exec api pytest tests/ -v --cov=app

# Locally
cd backend
pytest tests/ -v --cov=app
```

---

## 🌐 API Reference

| Endpoint | Method | Description | Auth |
| :--- | :---: | :--- | :---: |
| `/api/auth/register` | `POST` | Register a new user | 🔓 Free |
| `/api/auth/login` | `POST` | Authenticate & get session tokens | 🔓 Free |
| `/api/auth/refresh` | `POST` | Refresh access token (via HttpOnly Cookie) | 🔓 Free |
| `/api/auth/logout` | `DELETE` | Invalidate current user session | 🔒 Active |
| `/api/urls/shorten` | `POST` | Generate shortened link | 🔓/🔒 Opt |
| `/api/urls/` | `GET` | List user's shortened links (paginated) | 🔒 Active |
| `/api/urls/{short_code}` | `DELETE`| Deactivate a shortened link | 🔒 Owner |
| `/api/analytics/{short_code}/summary` | `GET` | Click summary & device analytics | 🔒 Owner |
| `/api/analytics/{short_code}/time-series`| `GET` | Retrieve clicks broken down by time series | 🔒 Owner |
| `/api/qr/{short_code}` | `GET` | Generate and fetch QR Code image | 🔒 Owner |
| `/{short_code}` | `GET` | Redirect to the original URL | 🔓 Free |

---

## 🛠️ Deployment Configuration

The repository is pre-configured with the following hosting integrations:
- **FastAPI Backend:** Deployed automatically to **Railway** via `railway.json`.
- **Next.js Frontend:** Deployed to **Vercel** with route redirects configuration in `vercel.json`.
- **Database & Cache:** Built for integration with **Supabase (PostgreSQL)** and **Redis Cloud**.
- **CI/CD Pipelines:** GitHub Actions (`.github/workflows/`) run test checkers on pull requests and trigger automatic deployment to production on merge to `main`.
