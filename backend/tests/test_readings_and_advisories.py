import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_readings_advisories_and_alert_deduping(client: AsyncClient, seed_test_hubs_and_users):
    tharaka = seed_test_hubs_and_users["tharaka"]

    # 1. Login as Tharaka Operator (language = 'sw')
    login_res = await client.post(
        "/api/v1/auth/login",
        data={"username": "op_tharaka", "password": "TharakaPass123!"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Batch: Moringa, 50 kg, target moisture = 10%
    b_res = await client.post(
        "/api/v1/batches/",
        headers=headers,
        json={
            "hub_id": str(tharaka.id),
            "crop_type": "moringa",
            "initial_weight_kg": 50.0,
            "target_moisture_pct": 10.0
        }
    )
    assert b_res.status_code == 201
    batch_id = b_res.json()["id"]

    # 3. Ingest reading 1: normal drying (moisture 25.0%, temp 45°C)
    r1_res = await client.post(
        "/api/v1/readings/",
        json={
            "batch_id": batch_id,
            "temperature": 45.0,
            "humidity": 40.0,
            "vpd": 1.5,
            "current_moisture": 25.0,
            "ambient_temperature": 28.0,
            "ambient_humidity": 50.0
        }
    )
    assert r1_res.status_code == 201

    # Check updated batch advisory is in Kiswahili
    batch_state1 = await client.get(f"/api/v1/batches/{batch_id}", headers=headers)
    b1_data = batch_state1.json()
    assert "Mzigo unakaushwa kawaida" in b1_data["latest_advisory"]

    # 4. Ingest reading 2: Near completion (moisture 10.8%, target 10.0%)
    r2_res = await client.post(
        "/api/v1/readings/",
        json={
            "batch_id": batch_id,
            "temperature": 48.0,
            "humidity": 35.0,
            "vpd": 1.8,
            "current_moisture": 10.8,
            "ambient_temperature": 29.0,
            "ambient_humidity": 45.0
        }
    )
    assert r2_res.status_code == 201

    # Check advisory changed to near_completion in Kiswahili
    batch_state2 = await client.get(f"/api/v1/batches/{batch_id}", headers=headers)
    b2_data = batch_state2.json()
    assert "unakaribia kiwango cha unyevu kinacholengwa" in b2_data["latest_advisory"]

    # Verify Alert was generated for near_completion
    alerts_res = await client.get(f"/api/v1/alerts/?batch_id={batch_id}", headers=headers)
    assert alerts_res.status_code == 200
    alerts = alerts_res.json()
    assert len(alerts) == 1
    assert alerts[0]["alert_type"] == "near_completion"

    # 5. Ingest reading 3: Still near completion (moisture 10.5%) -> Deduping check!
    r3_res = await client.post(
        "/api/v1/readings/",
        json={
            "batch_id": batch_id,
            "temperature": 48.0,
            "humidity": 35.0,
            "vpd": 1.8,
            "current_moisture": 10.5,
            "ambient_temperature": 29.0,
            "ambient_humidity": 45.0
        }
    )
    assert r3_res.status_code == 201

    # Verify no second near_completion alert was sent!
    alerts_res2 = await client.get(f"/api/v1/alerts/?batch_id={batch_id}", headers=headers)
    assert len(alerts_res2.json()) == 1

    # 6. Ingest reading 4: Over-drying penalty check (moisture drops to 6.0%, target was 10.0% -> penalty < 7.5%)
    r4_res = await client.post(
        "/api/v1/readings/",
        json={
            "batch_id": batch_id,
            "temperature": 50.0,
            "humidity": 30.0,
            "vpd": 2.1,
            "current_moisture": 6.0,
            "ambient_temperature": 30.0,
            "ambient_humidity": 40.0
        }
    )
    assert r4_res.status_code == 201
    batch_state4 = await client.get(f"/api/v1/batches/{batch_id}", headers=headers)
    assert batch_state4.json()["predicted_quality_grade"] == "downgraded"

