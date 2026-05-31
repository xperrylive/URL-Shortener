"""
Analytics Router.

Endpoints:
  GET /api/analytics/{short_code}/summary      → Total clicks, unique countries, top device
  GET /api/analytics/{short_code}/clicks       → Paginated click history
  GET /api/analytics/{short_code}/time-series  → Clicks per day (7 or 30 days)
  GET /api/analytics/{short_code}/countries    → Click breakdown by country
  GET /api/analytics/{short_code}/devices      → Click breakdown by device type
  GET /api/analytics/{short_code}/referrers    → Top referrers
  GET /api/analytics/dashboard                 → Aggregate stats across all user URLs
"""
