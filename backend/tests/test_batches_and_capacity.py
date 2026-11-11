import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_batch_creation_and_capacity_constraints(client: AsyncClient, seed_test_hubs_and_users):
    meru = seed_test_hubs_and_users["meru"]

    # 1. Login as Meru Operator
    login_res = await client.post(
        "/api/v1/auth/login",
        data={"username": "op_meru", "password": "MeruPass123!"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Batch 1: 100 kg Moringa
    b1_res = await client.post(
        "/api/v1/batches/",
        headers=headers,
        json={
            "hub_id": str(meru.id),
            "crop_type": "moringa",
            "initial_weight_kg": 100.0
        }
    )
    assert b1_res.status_code == 201
    b1_data = b1_res.json()
    assert b1_data["crop_type"] == "moringa"
    assert b1_data["initial_weight_kg"] == 100.0
    assert b1_data["target_moisture_pct"] == 10.0  # default for moringa
    b1_id = b1_data["id"]

    # 3. Create Batch 2: 80 kg Hibiscus (concurrent in same dryer: 100 + 80 = 180 <= 200)
    b2_res = await client.post(
        "/api/v1/batches/",
        headers=headers,
        json={
            "hub_id": str(meru.id),
            "crop_type": "hibiscus",
            "initial_weight_kg": 80.0
        }
    )
    assert b2_res.status_code == 201
    b2_data = b2_res.json()
    assert b2_data["target_moisture_pct"] == 11.0  # default for hibiscus

    # 4. Attempt Batch 3: 30 kg (180 + 30 = 210 > 200 capacity) -> Must fail with HTTP 400
    b3_fail_res = await client.post(
        "/api/v1/batches/",
        headers=headers,
        json={
            "hub_id": str(meru.id),
            "crop_type": "prunus",
            "initial_weight_kg": 30.0
        }
    )
    assert b3_fail_res.status_code == 400
    assert "Dryer capacity exceeded" in b3_fail_res.json()["detail"]

    # 5. Complete Batch 1 (100 kg removed, active load drops to 80 kg)
    complete_res = await client.post(
        f"/api/v1/batches/{b1_id}/complete",
        headers=headers
    )
    assert complete_res.status_code == 200
    assert complete_res.json()["status"] == "completed"

    # 6. Retry Batch 3: 30 kg (now 80 + 30 = 110 <= 200) -> Must succeed!
    b3_success_res = await client.post(
        "/api/v1/batches/",
        headers=headers,
        json={
            "hub_id": str(meru.id),
            "crop_type": "prunus",
            "initial_weight_kg": 30.0
        }
    )
    assert b3_success_res.status_code == 201
    assert b3_success_res.json()["crop_type"] == "prunus"
    assert b3_success_res.json()["target_moisture_pct"] == 12.0  # default for prunus

