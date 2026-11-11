import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, seed_test_hubs_and_users):
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "AdminPass123!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, seed_test_hubs_and_users):
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "WrongPassword"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, seed_test_hubs_and_users):
    # Login as op_meru
    login_res = await client.post(
        "/api/v1/auth/login",
        data={"username": "op_meru", "password": "MeruPass123!"}
    )
    token = login_res.json()["access_token"]

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["username"] == "op_meru"
    assert user_data["role"] == "operator"
    assert user_data["preferred_language"] == "en"

