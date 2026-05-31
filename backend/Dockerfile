# ─────────────────────────────────────────
# URL Shortener Backend — Production Image
# ─────────────────────────────────────────
FROM python:3.11-slim AS base

# Prevent Python from writing .pyc files and enable stdout/stderr flushing
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install OS dependencies (needed by asyncpg + Pillow + geoip2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Expose the port Uvicorn will bind to
EXPOSE 8000

# Default command — Railway injects PORT env var; we default to 8000 locally
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
