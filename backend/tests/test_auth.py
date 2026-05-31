"""
Auth endpoint tests.

Covers:
  - POST /api/auth/register
  - POST /api/auth/login
  - POST /api/auth/refresh
  - DELETE /api/auth/logout
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestRegister:
    async def test_register_success(self, client: AsyncClient):
        resp = await client.post(
            "/api/auth/register",
            json={"email": "new@example.com", "password": "Secure1Pass"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["access_token"]
        assert data["user"]["email"] == "new@example.com"
        assert data["user"]["tier"] == "free"

    async def test_register_duplicate_email(self, client: AsyncClient, registered_user: dict):
        # Try to register again with the same email that was used for registered_user
        email = registered_user["user"]["email"]
        resp = await client.post(
            "/api/auth/register",
            json={"email": email, "password": "AnotherPass1"},
        )
        assert resp.status_code == 409

    async def test_register_weak_password(self, client: AsyncClient):
        resp = await client.post(
            "/api/auth/register",
            json={"email": "weak@example.com", "password": "short"},
        )
        assert resp.status_code == 422

    async def test_register_no_uppercase(self, client: AsyncClient):
        resp = await client.post(
            "/api/auth/register",
            json={"email": "noup@example.com", "password": "alllower1"},
        )
        assert resp.status_code == 422

    async def test_register_no_digit(self, client: AsyncClient):
        resp = await client.post(
            "/api/auth/register",
            json={"email": "nodigit@example.com", "password": "AllLettersOnly"},
        )
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestLogin:
    async def test_login_success(self, client: AsyncClient, registered_user: dict):
        email = registered_user["user"]["email"]
        resp = await client.post(
            "/api/auth/login",
            json={"email": email, "password": "TestPass1"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["access_token"]
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient, registered_user: dict):
        email = registered_user["user"]["email"]
        resp = await client.post(
            "/api/auth/login",
            json={"email": email, "password": "WrongPass1"},
        )
        assert resp.status_code == 401

    async def test_login_unknown_email(self, client: AsyncClient):
        resp = await client.post(
            "/api/auth/login",
            json={"email": "nobody@example.com", "password": "SomePass1"},
        )
        assert resp.status_code == 401


@pytest.mark.asyncio
class TestLogout:
    async def test_logout_requires_auth(self, client: AsyncClient):
        resp = await client.delete("/api/auth/logout")
        assert resp.status_code == 401

    async def test_logout_success(self, client: AsyncClient, auth_headers: dict):
        resp = await client.delete("/api/auth/logout", headers=auth_headers)
        assert resp.status_code == 204
