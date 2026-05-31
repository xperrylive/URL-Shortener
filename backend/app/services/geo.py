"""
GeoIP Service.

Resolves IP addresses to country and city using:
  - geoip2 Python library
  - MaxMind GeoLite2-City.mmdb database file (path from GEOIP_DB_PATH env var)
"""
