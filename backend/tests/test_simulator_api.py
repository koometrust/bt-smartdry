import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.batch import Batch


@pytest.mark.asyncio
async def test_simulator_auth_guards(client: AsyncClient):
    # Unauthenticated requests must be rejected with 401
    res_status = await client.get("/api/v1/simulator/status")
    assert res_status.status_code == 401

    res_start = await client.post("/api/v1/simulator/start")
    assert res_start.status_code == 401

    res_stop = await client.post("/api/v1/simulator/stop")
    assert res_stop.status_code == 401


@pytest.mark.asyncio
async def test_simulator_lifecycle_and_status(
    client: AsyncClient,
    seed_test_hubs_and_users,
    db_session: AsyncSession
):
    meru = seed_test_hubs_and_users["meru"]
    op_meru = seed_test_hubs_and_users["op_meru"]

    # Create active batch
    batch = Batch(
        hub_id=meru.id,
        crop_type="moringa",
        initial_weight_kg=60.0,
        target_moisture_pct=10.0,
        status="active",
        created_by_user_id=op_meru.id
    )
    db_session.add(batch)
    await db_session.commit()

    # Login as Operator
    op_login = await client.post(
        "/api/v1/auth/login",
        data={"username": "op_meru", "password": "MeruPass123!"}
    )
    token = op_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Initial status: idle
    status_res = await client.get("/api/v1/simulator/status", headers=headers)
    assert status_res.status_code == 200
    data = status_res.json()
    assert "is_running" in data
    assert "active_batches_count" in data

    # 2. Start simulator
    start_res = await client.post(
        "/api/v1/simulator/start",
        headers=headers,
        json={"interval_seconds": 0.5, "speedup": 0.35}
    )
    assert start_res.status_code == 200
    start_data = start_res.json()
    assert start_data["is_running"] is True

    # Allow simulator task to tick briefly
    await asyncio.sleep(0.6)

    # 3. Check status while running
    running_status = await client.get("/api/v1/simulator/status", headers=headers)
    assert running_status.status_code == 200
    r_data = running_status.json()
    assert r_data["is_running"] is True

    # 4. Stop simulator
    stop_res = await client.post("/api/v1/simulator/stop", headers=headers)
    assert stop_res.status_code == 200
    stop_data = stop_res.json()
    assert stop_data["is_running"] is False

    # 5. Confirm idle status
    final_status = await client.get("/api/v1/simulator/status", headers=headers)
    assert final_status.json()["is_running"] is False

