import pytest
import time
from httpx import AsyncClient

from app.schemas.batch import QualityGrade
from app.services.ml_service import MLService, get_ml_service


def test_ml_service_artifact_loading():
    service = get_ml_service()
    assert service.load_models() is True
    assert service.is_loaded is True
    assert service.regressor is not None
    assert service.classifier is not None


def test_ml_service_prediction_latency_and_output():
    service = get_ml_service()
    if not service.is_loaded:
        service.load_models()

    features = {
        "temperature": 45.0,
        "humidity": 35.0,
        "vpd": 2.1,
        "current_moisture": 22.0,
        "batch_weight": 50.0,
        "elapsed_hours": 3.5,
        "ambient_temperature": 27.0,
        "ambient_humidity": 50.0,
        "crop_type": "moringa",
        "hub_location": "meru",
    }

    # Warm-up call
    service.predict(features, fallback_target_moisture=10.0)

    start = time.perf_counter()
    rem_hours, grade = service.predict(features, fallback_target_moisture=10.0)
    latency_ms = (time.perf_counter() - start) * 1000.0

    assert latency_ms < 100.0, f"Inference took too long: {latency_ms:.2f} ms"
    assert isinstance(rem_hours, float)
    assert rem_hours >= 0.0
    assert isinstance(grade, QualityGrade)


def test_ml_service_fallback_when_models_missing(tmp_path):
    # Empty directory
    fallback_service = MLService(models_dir=tmp_path)
    assert fallback_service.load_models() is False
    assert fallback_service.is_loaded is False

    features = {
        "temperature": 40.0,
        "humidity": 50.0,
        "vpd": 1.5,
        "current_moisture": 25.0,
        "batch_weight": 50.0,
        "crop_type": "moringa",
        "hub_location": "meru",
    }
    rem_hours, grade = fallback_service.predict(features, fallback_target_moisture=10.0)
    assert rem_hours > 0.0
    assert grade in [QualityGrade.EXPORT, QualityGrade.STANDARD, QualityGrade.DOWNGRADED]


@pytest.mark.asyncio
async def test_reading_endpoint_updates_batch_ml_predictions(client: AsyncClient, seed_test_hubs_and_users):
    meru = seed_test_hubs_and_users["meru"]

    login_res = await client.post(
        "/api/v1/auth/login",
        data={"username": "op_meru", "password": "MeruPass123!"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create batch
    b_res = await client.post(
        "/api/v1/batches/",
        headers=headers,
        json={
            "hub_id": str(meru.id),
            "crop_type": "hibiscus",
            "initial_weight_kg": 60.0,
            "target_moisture_pct": 10.0
        }
    )
    assert b_res.status_code == 201
    batch_id = b_res.json()["id"]

    # Ingest reading
    r_res = await client.post(
        "/api/v1/readings/",
        json={
            "batch_id": batch_id,
            "temperature": 48.0,
            "humidity": 30.0,
            "vpd": 2.5,
            "current_moisture": 18.0,
            "ambient_temperature": 26.0,
            "ambient_humidity": 45.0
        }
    )
    assert r_res.status_code == 201

    # Fetch batch to check ML snapshot fields
    detail_res = await client.get(f"/api/v1/batches/{batch_id}", headers=headers)
    assert detail_res.status_code == 200
    batch_data = detail_res.json()

    assert batch_data["predicted_remaining_hours"] is not None
    assert batch_data["predicted_remaining_hours"] >= 0.0
    assert batch_data["predicted_quality_grade"] in ["export", "standard", "downgraded"]
    assert batch_data["latest_advisory"] is not None
