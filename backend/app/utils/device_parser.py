"""
Device Parser Utility.

Parses a User-Agent string and returns a normalised device type:
    "mobile"   → phones, tablets
    "desktop"  → traditional computers
    "bot"      → crawlers, scrapers, monitoring agents
    "unknown"  → unrecognised UA strings or empty

Uses the `user-agents` library (wraps ua-parser).
Falls back to simple keyword matching when the library is unavailable.
"""
from __future__ import annotations

try:
    from user_agents import parse as _ua_parse  # type: ignore

    def get_device_type(user_agent_string: str | None) -> str:
        """Return device type string from a raw User-Agent header value."""
        if not user_agent_string:
            return "unknown"
        ua = _ua_parse(user_agent_string)
        if ua.is_bot:
            return "bot"
        if ua.is_mobile or ua.is_tablet:
            return "mobile"
        if ua.is_pc:
            return "desktop"
        return "unknown"

except ImportError:
    # Fallback — no external dependency required
    _BOT_KEYWORDS = (
        "bot", "crawl", "spider", "slurp", "facebookexternalhit",
        "twitterbot", "linkedinbot", "googlebot", "bingbot",
        "ahrefsbot", "semrushbot", "datadog", "pingdom", "uptimerobot",
    )
    _MOBILE_KEYWORDS = (
        "mobile", "android", "iphone", "ipad", "ipod",
        "blackberry", "windows phone", "opera mini",
    )

    def get_device_type(user_agent_string: str | None) -> str:  # type: ignore[misc]
        if not user_agent_string:
            return "unknown"
        ua_lower = user_agent_string.lower()
        if any(kw in ua_lower for kw in _BOT_KEYWORDS):
            return "bot"
        if any(kw in ua_lower for kw in _MOBILE_KEYWORDS):
            return "mobile"
        # Heuristic: if it has "mozilla" it's likely a browser on desktop
        if "mozilla" in ua_lower:
            return "desktop"
        return "unknown"
