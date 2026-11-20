import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from app.models.batch import Batch
from uuid import UUID


@pytest.mark.asyncio
async def test_batch_completion_calculates_and_persists_avoided_loss(
    client: AsyncClient,
    seed_test_hubs_and_users,
    db_session: AsyncSession
):
    meru = seed_test_hubs_and_users["meru"]

    # 1. Login as Meru Operator
    login_res = await client.post(
        "/api/v1/auth/login",
        data={"username": "op_meru", "password": "MeruPass123!"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Batch: 100 kg Moringa
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
    b1_id = b1_res.json()["id"]

    # Manually set quality grade to export in db to test grade multiplier
    await db_session.execute(
        update(Batch)
        .where(Batch.id == UUID(b1_id))
        .values(predicted_quality_grade="export")
    )
    await db_session.commit()

    # 3. Complete batch via PATCH /api/v1/batches/{id}/complete
    complete_res = await client.patch(
        f"/api/v1/batches/{b1_id}/complete",
        headers=headers
    )
    assert complete_res.status_code == 200
    data = complete_res.json()
    assert data["status"] == "completed"
    # Moringa 100 kg export:
    # kg_saved = 100 * (0.35 - 0.05) = 30.0 kg
    # kes_saved = 30.0 * 300 * 1.0 = 9000.0 KES
    assert data["avoided_loss_kg"] == 30.0
    assert data["avoided_loss_kes"] == 9000.0

    # 4. Verify fetch get_batch returns the loss metrics
    get_res = await client.get(
        f"/api/v1/batches/{b1_id}",
        headers=headers
    )
    assert get_res.status_code == 200
    fetched = get_res.json()
    assert fetched["avoided_loss_kg"] == 30.0
    assert fetched["avoided_loss_kes"] == 9000.0


@pytest.mark.asyncio
async def test_analytics_overview_aggregates_avoided_loss(
    client: AsyncClient,
    seed_test_hubs_and_users,
    db_session: AsyncSession
):
    meru = seed_test_hubs_and_users["meru"]

    # 1. Login as Admin
    admin_login = await client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "AdminPass123!"}
    )
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Login as Operator to create & complete batches
    op_login = await client.post(
        "/api/v1/auth/login",
        data={"username": "op_meru", "password": "MeruPass123!"}
    )
    op_token = op_login.json()["access_token"]
    op_headers = {"Authorization": f"Bearer {op_token}"}

    # Create & complete Batch 1: 50 kg Prunus Standard
    # 50 * (0.30 - 0.04) = 13 kg saved. 13 * 450 * 0.9 = 5265 KES
    b1_res = await client.post(
        "/api/v1/batches/",
        headers=op_headers,
        json={
            "hub_id": str(meru.id),
            "crop_type": "prunus",
            "initial_weight_kg": 50.0
        }
    )
    b1_id = b1_res.json()["id"]
    await db_session.execute(
        update(Batch)
        .where(Batch.id == UUID(b1_id))
        .values(predicted_quality_grade="standard")
    )
    await db_session.commit()

    await client.post(f"/api/v1/batches/{b1_id}/complete", headers=op_headers)

    # 3. Query GET /api/v1/analytics/overview as Admin
    analytics_res = await client.get(
        "/api/v1/analytics/overview",
        headers=admin_headers
    )
    assert analytics_res.status_code == 200
    analytics_data = analytics_res.json()
    assert "total_avoided_loss_kg" in analytics_data
    assert "total_avoided_loss_kes" in analytics_data
    assert analytics_data["total_avoided_loss_kg"] >= 13.0
    assert analytics_data["total_avoided_loss_kes"] >= 5265.0
    assert "crop_breakdown" in analytics_data
    assert "hub_breakdown" in analytics_data
