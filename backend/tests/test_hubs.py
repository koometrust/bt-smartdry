import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_hubs(client: AsyncClient, seed_test_hubs_and_users):
    login_res = await client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "AdminPass123!"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/hubs/", headers=headers)
    assert response.status_code == 200
    hubs = response.json()
    assert len(hubs) == 3
    hub_names = [h["name"] for h in hubs]
    assert "Meru" in hub_names
    assert "Tharaka Nithi" in hub_names
    assert "Eldoret" in hub_names
    for h in hubs:
        assert h["dryer_capacity_kg"] == 200.0


@pytest.mark.asyncio
async def test_create_hub_admin_only(client: AsyncClient, seed_test_hubs_and_users):
    # 1. Non-admin operator cannot create hub
    op_login = await client.post(
        "/api/v1/auth/login",
        data={"username": "op_meru", "password": "MeruPass123!"}
    )
    op_token = op_login.json()["access_token"]
    fail_res = await client.post(
        "/api/v1/hubs/",
        headers={"Authorization": f"Bearer {op_token}"},
        json={"name": "Kitui", "location": "Kitui County", "dryer_capacity_kg": 200.0}
    )
    assert fail_res.status_code == 403

    # 2. Admin can create hub
    admin_login = await client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "AdminPass123!"}
    )
    admin_token = admin_login.json()["access_token"]
    success_res = await client.post(
        "/api/v1/hubs/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Kitui", "location": "Kitui County", "dryer_capacity_kg": 200.0}
    )
    assert success_res.status_code == 201
    assert success_res.json()["name"] == "Kitui"

