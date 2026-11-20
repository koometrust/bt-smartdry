import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.batch import Batch
from app.models.alert import Alert
from app.models.user import User
from app.core.config import settings
from app.services.alert_service import trigger_alert_if_needed
from app.schemas.alert import AlertType, AlertStatus


@pytest.mark.asyncio
async def test_sms_provider_mode_config():
    assert hasattr(settings, "SMS_PROVIDER_MODE")
    assert settings.SMS_PROVIDER_MODE in ["mock", "sandbox", "live"]


@pytest.mark.asyncio
async def test_alert_service_mock_mode(db_session: AsyncSession, seed_test_hubs_and_users):
    meru = seed_test_hubs_and_users["meru"]
    op_meru = seed_test_hubs_and_users["op_meru"]

    batch = Batch(
        hub_id=meru.id,
        crop_type="moringa",
        initial_weight_kg=80.0,
        target_moisture_pct=10.0,
        status="active",
        created_by_user_id=op_meru.id
    )
    db_session.add(batch)
    await db_session.commit()
    await db_session.refresh(batch)

    # In mock mode, alert is recorded as sent
    alert = await trigger_alert_if_needed(
        db=db_session,
        batch=batch,
        alert_type=AlertType.NEAR_COMPLETION,
        message="Batch near completion mock test"
    )
    assert alert is not None
    assert alert.status == AlertStatus.SENT.value
    assert alert.is_read is False
    assert alert.phone_number == op_meru.phone_number


@pytest.mark.asyncio
async def test_alerts_role_scoping_and_filtering(
    client: AsyncClient,
    seed_test_hubs_and_users,
    db_session: AsyncSession
):
    meru = seed_test_hubs_and_users["meru"]
    tharaka = seed_test_hubs_and_users["tharaka"]
    op_meru = seed_test_hubs_and_users["op_meru"]
    op_tharaka = seed_test_hubs_and_users["op_tharaka"]

    # Create batch 1 in Meru
    batch_meru = Batch(
        hub_id=meru.id,
        crop_type="moringa",
        initial_weight_kg=50.0,
        target_moisture_pct=10.0,
        status="active",
        created_by_user_id=op_meru.id
    )
    # Create batch 2 in Tharaka
    batch_tharaka = Batch(
        hub_id=tharaka.id,
        crop_type="hibiscus",
        initial_weight_kg=40.0,
        target_moisture_pct=11.0,
        status="active",
        created_by_user_id=op_tharaka.id
    )
    db_session.add_all([batch_meru, batch_tharaka])
    await db_session.commit()

    # Trigger alert for Meru batch
    alert_meru = await trigger_alert_if_needed(
        db=db_session,
        batch=batch_meru,
        alert_type=AlertType.NEAR_COMPLETION,
        message="Meru Near Completion"
    )
    # Trigger alert for Tharaka batch
    alert_tharaka = await trigger_alert_if_needed(
        db=db_session,
        batch=batch_tharaka,
        alert_type=AlertType.ANOMALY,
        message="Tharaka High Humidity"
    )

    # 1. Login as Meru Operator
    op_login = await client.post(
        "/api/v1/auth/login",
        data={"username": "op_meru", "password": "MeruPass123!"}
    )
    op_token = op_login.json()["access_token"]
    op_headers = {"Authorization": f"Bearer {op_token}"}

    # Meru Operator should see Meru alert, but NOT Tharaka alert
    alerts_res = await client.get("/api/v1/alerts/", headers=op_headers)
    assert alerts_res.status_code == 200
    alerts_data = alerts_res.json()
    meru_batch_ids = [a["batch_id"] for a in alerts_data]
    assert str(batch_meru.id) in meru_batch_ids
    assert str(batch_tharaka.id) not in meru_batch_ids

    # Unread count for Meru operator should be 1
    unread_res = await client.get("/api/v1/alerts/unread-count", headers=op_headers)
    assert unread_res.status_code == 200
    assert unread_res.json()["unread_count"] == 1

    # Mark Meru alert as read
    read_res = await client.post(f"/api/v1/alerts/{alert_meru.id}/read", headers=op_headers)
    assert read_res.status_code == 200
    assert read_res.json()["is_read"] is True

    # Unread count should now be 0
    unread_res2 = await client.get("/api/v1/alerts/unread-count", headers=op_headers)
    assert unread_res2.json()["unread_count"] == 0

    # 2. Login as Admin
    admin_login = await client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "AdminPass123!"}
    )
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Admin should see both alerts across hubs
    admin_alerts_res = await client.get("/api/v1/alerts/", headers=admin_headers)
    assert admin_alerts_res.status_code == 200
    admin_batch_ids = [a["batch_id"] for a in admin_alerts_res.json()]
    assert str(batch_meru.id) in admin_batch_ids
    assert str(batch_tharaka.id) in admin_batch_ids

    # Admin filtering by alert_type
    filter_type_res = await client.get(
        "/api/v1/alerts/?alert_type=anomaly",
        headers=admin_headers
    )
    assert filter_type_res.status_code == 200
    anomaly_alerts = filter_type_res.json()
    assert len(anomaly_alerts) == 1
    assert anomaly_alerts[0]["alert_type"] == "anomaly"

    # Admin filtering by hub_id
    filter_hub_res = await client.get(
        f"/api/v1/alerts/?hub_id={meru.id}",
        headers=admin_headers
    )
    assert filter_hub_res.status_code == 200
    hub_alerts = filter_hub_res.json()
    assert all(a["batch_id"] == str(batch_meru.id) for a in hub_alerts)

