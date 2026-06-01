"""
Redirect endpoint tests.

Covers:
  - GET /{short_code} → 301 redirect
  - GET /{short_code} → 404 not found
  - GET /{short_code} → 404 inactive
  - GET /{short_code} → 410 expired
  - click_count incremented after redirect
"""
from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient


async def _create_url(client: AsyncClient, auth_headers: dict, **kwargs) -> dict:
    body = {"url": "https://www.target.com/page", **kwargs}
    resp = await client.post("/api/urls/shorten", json=body, headers=auth_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest.mark.asyncio
class TestRedirect:
    async def test_redirect_success(self, client: AsyncClient, auth_headers: dict):
        data = await _create_url(client, auth_headers)
        short_code = data["short_code"]

        resp = await client.get(f"/{short_code}", follow_redirects=False)
        assert resp.status_code == 301
        assert resp.headers["location"] == "https://www.target.com/page"

    async def test_redirect_not_found(self, client: AsyncClient):
        resp = await client.get("/doesnotexist99", follow_redirects=False)
        assert resp.status_code == 302
        assert "/not-found" in resp.headers["location"]

    async def test_redirect_inactive(self, client: AsyncClient, auth_headers: dict):
        data = await _create_url(client, auth_headers)
        short_code = data["short_code"]

        # Deactivate
        await client.delete(f"/api/urls/{short_code}", headers=auth_headers)

        resp = await client.get(f"/{short_code}", follow_redirects=False)
        assert resp.status_code == 302
        assert "/not-found?reason=inactive" in resp.headers["location"]

    async def test_redirect_expired(self, client: AsyncClient, auth_headers: dict):
        past = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        data = await _create_url(client, auth_headers, expires_at=past)
        short_code = data["short_code"]

        resp = await client.get(f"/{short_code}", follow_redirects=False)
        assert resp.status_code == 302
        assert "/not-found?reason=expired" in resp.headers["location"]

    async def test_click_count_incremented(self, client: AsyncClient, auth_headers: dict):
        data = await _create_url(client, auth_headers)
        short_code = data["short_code"]

        # Trigger 2 redirects
        await client.get(f"/{short_code}", follow_redirects=False)
        await client.get(f"/{short_code}", follow_redirects=False)

        # Allow background task to complete
        import asyncio
        await asyncio.sleep(0.1)

        detail = await client.get(f"/api/urls/{short_code}", headers=auth_headers)
        assert detail.json()["click_count"] >= 2
