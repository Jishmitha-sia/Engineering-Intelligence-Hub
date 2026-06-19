"""Integration tests for authentication API."""

import pytest


@pytest.mark.integration
@pytest.mark.auth
class TestAuthAPI:
    @pytest.mark.asyncio
    async def test_register_and_login(self, client, sample_user):
        register_response = await client.post(
            "/api/v1/auth/register",
            json=sample_user,
        )
        assert register_response.status_code == 201
        register_data = register_response.json()
        assert register_data["success"] is True
        assert "access_token" in register_data["data"]
        assert register_data["data"]["user"]["email"] == sample_user["email"]

        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": sample_user["email"],
                "password": sample_user["password"],
            },
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert login_data["success"] is True
        token = login_data["data"]["access_token"]

        me_response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_response.status_code == 200
        assert me_response.json()["email"] == sample_user["email"]

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client, sample_user):
        await client.post("/api/v1/auth/register", json=sample_user)
        duplicate_response = await client.post(
            "/api/v1/auth/register",
            json=sample_user,
        )
        assert duplicate_response.status_code == 400

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client, sample_user):
        await client.post("/api/v1/auth/register", json=sample_user)
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": sample_user["email"],
                "password": "WrongPass123!",
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_protected_route_without_token(self, client):
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 403
