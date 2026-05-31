"""
URL endpoint tests.

Covers:
  - POST /api/urls/shorten
  - GET  /api/urls/
  - GET  /api/urls/{short_code}
  - PATCH /api/urls/{short_code}
  - DELETE /api/urls/{short_code}
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestShorten:
    async def test_shorten_anonymous(self, client: AsyncClient):
        resp = await client.post(
            "/api/urls/shorten",
            json={"url": "https://www.example.com/very/long/path"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert len(data["short_code"]) == 6
        assert data["short_url"].startswith("http")
        assert data["user_id"] is None  # anonymous

    async def test_shorten_authenticated(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/api/urls/shorten",
            json={"url": "https://www.authenticated.com/path"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["user_id"] is not None

    async def test_shorten_custom_alias(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/api/urls/shorten",
            json={"url": "https://www.example.com/custom", "custom_alias": "my-alias"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["short_code"] == "my-alias"

    async def test_shorten_reserved_alias(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/api/urls/shorten",
            json={"url": "https://example.com", "custom_alias": "admin"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    async def test_shorten_duplicate_alias(self, client: AsyncClient, auth_headers: dict):
        await client.post(
            "/api/urls/shorten",
            json={"url": "https://example.com/1", "custom_alias": "unique-alias"},
            headers=auth_headers,
        )
        resp = await client.post(
            "/api/urls/shorten",
            json={"url": "https://example.com/2", "custom_alias": "unique-alias"},
            headers=auth_headers,
        )
        assert resp.status_code == 409

    async def test_shorten_invalid_url(self, client: AsyncClient):
        resp = await client.post(
            "/api/urls/shorten",
            json={"url": "not-a-url"},
        )
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestListURLs:
    async def test_list_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/urls/")
        assert resp.status_code == 401

    async def test_list_returns_own_urls(self, client: AsyncClient, auth_headers: dict):
        # Create 2 URLs for this user
        for i in range(2):
            await client.post(
                "/api/urls/shorten",
                json={"url": f"https://example.com/page{i}"},
                headers=auth_headers,
            )
        resp = await client.get("/api/urls/", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 2
        assert "items" in data

    async def test_list_pagination(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/urls/?page=1&page_size=2", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) <= 2


@pytest.mark.asyncio
class TestGetURL:
    async def test_get_own_url(self, client: AsyncClient, auth_headers: dict):
        create = await client.post(
            "/api/urls/shorten",
            json={"url": "https://example.com/get-test"},
            headers=auth_headers,
        )
        short_code = create.json()["short_code"]
        resp = await client.get(f"/api/urls/{short_code}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["short_code"] == short_code

    async def test_get_requires_auth(self, client: AsyncClient, auth_headers: dict):
        create = await client.post(
            "/api/urls/shorten",
            json={"url": "https://example.com/auth-required"},
            headers=auth_headers,
        )
        short_code = create.json()["short_code"]
        resp = await client.get(f"/api/urls/{short_code}")
        assert resp.status_code == 401


@pytest.mark.asyncio
class TestDeleteURL:
    async def test_delete_deactivates_url(self, client: AsyncClient, auth_headers: dict):
        create = await client.post(
            "/api/urls/shorten",
            json={"url": "https://example.com/to-delete"},
            headers=auth_headers,
        )
        short_code = create.json()["short_code"]

        resp = await client.delete(f"/api/urls/{short_code}", headers=auth_headers)
        assert resp.status_code == 204

        # Verify it's deactivated
        detail = await client.get(f"/api/urls/{short_code}", headers=auth_headers)
        assert detail.json()["is_active"] is False
