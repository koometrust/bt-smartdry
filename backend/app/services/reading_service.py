from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.batch import Batch
from app.models.hub import Hub
from app.models.reading import Reading
from app.models.user import User
from app.schemas.reading import ReadingCreate, ReadingResponse
from app.schemas.alert import AlertType
from app.schemas.batch import BatchStatus, QualityGrade
from app.services.advisory_service import generate_advisory
from app.services.alert_service import trigger_alert_if_needed
from app.services.ml_service import get_ml_service


async def add_reading(
    db: AsyncSession,
    reading_in: ReadingCreate
) -> ReadingResponse:
    # 1. Fetch batch
    batch = await db.get(Batch, reading_in.batch_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch with ID {reading_in.batch_id} not found."
        )

    if batch.status != BatchStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot add readings to completed batch {batch.id}."
        )

    # 2. Persist Reading
    reading = Reading(
        batch_id=batch.id,
        timestamp=reading_in.timestamp or datetime.now(timezone.utc),
        temperature=reading_in.temperature,
        humidity=reading_in.humidity,
        vpd=reading_in.vpd,
        current_moisture=reading_in.current_moisture,
        ambient_temperature=reading_in.ambient_temperature,
        ambient_humidity=reading_in.ambient_humidity
    )
    db.add(reading)

    # 3. Predict / Estimate Remaining Hours & Grade (via Embedded ML Service)
    hub = await db.get(Hub, batch.hub_id)
    hub_location = hub.location.lower() if hub else "meru"
    
    t_reading = reading.timestamp.replace(tzinfo=timezone.utc) if reading.timestamp.tzinfo is None else reading.timestamp
    t_start = batch.start_time.replace(tzinfo=timezone.utc) if batch.start_time.tzinfo is None else batch.start_time
    elapsed_seconds = max(0.0, (t_reading - t_start).total_seconds())
    elapsed_hours = round(elapsed_seconds / 3600.0, 4)

    ml_features = {
        "temperature": reading.temperature,
        "humidity": reading.humidity,
        "vpd": reading.vpd,
        "current_moisture": reading.current_moisture,
        "batch_weight": batch.initial_weight_kg,
        "elapsed_hours": elapsed_hours,
        "ambient_temperature": reading.ambient_temperature,
        "ambient_humidity": reading.ambient_humidity,
        "crop_type": batch.crop_type.lower(),
        "hub_location": hub_location,
    }

    ml_service = get_ml_service()
    remaining_hours, predicted_grade = ml_service.predict(
        ml_features,
        fallback_target_moisture=batch.target_moisture_pct
    )
    hours = int(remaining_hours)
    mins = int((remaining_hours - hours) * 60)

    batch.predicted_remaining_hours = round(remaining_hours, 2)
    batch.predicted_quality_grade = predicted_grade.value

    # 4. Determine user language preference
    user_lang = "en"
    if batch.created_by_user_id:
        user = await db.get(User, batch.created_by_user_id)
        if user and user.preferred_language:
            user_lang = user.preferred_language

    # 5. Advisory & Alert Evaluation
    advisory_msg = ""
    # Check Anomaly
    if reading.temperature > 60.0:
        advisory_msg = generate_advisory("anomaly_overheating", lang=user_lang, temp=round(reading.temperature, 1))
        await trigger_alert_if_needed(db, batch, AlertType.ANOMALY, advisory_msg)
    elif reading.humidity > 85.0:
        advisory_msg = generate_advisory("anomaly_high_humidity", lang=user_lang, humidity=round(reading.humidity, 1))
        await trigger_alert_if_needed(db, batch, AlertType.ANOMALY, advisory_msg)
    # Check Completion
    elif reading.current_moisture <= batch.target_moisture_pct:
        advisory_msg = generate_advisory(
            "completed",
            lang=user_lang,
            moisture=round(reading.current_moisture, 1),
            grade=predicted_grade.value.capitalize()
        )
        await trigger_alert_if_needed(db, batch, AlertType.COMPLETION, advisory_msg)
    # Check Near Completion (< 30 min or moisture diff < 1.5%)
    elif remaining_hours <= 0.5 or (reading.current_moisture - batch.target_moisture_pct) <= 1.5:
        advisory_msg = generate_advisory(
            "near_completion",
            lang=user_lang,
            moisture=round(reading.current_moisture, 1),
            mins=max(5, mins)
        )
        await trigger_alert_if_needed(db, batch, AlertType.NEAR_COMPLETION, advisory_msg)
    else:
        advisory_msg = generate_advisory(
            "normal_drying",
            lang=user_lang,
            hours=hours,
            mins=mins,
            grade=predicted_grade.value.capitalize()
        )

    batch.latest_advisory = advisory_msg

    await db.commit()
    await db.refresh(reading)

    return ReadingResponse.model_validate(reading)


async def get_batch_readings(
    db: AsyncSession,
    batch_id: UUID,
    limit: int = 100
) -> List[ReadingResponse]:
    query = select(Reading).where(
        Reading.batch_id == batch_id
    ).order_by(Reading.timestamp.desc()).limit(limit)
    
    result = await db.execute(query)
    readings = result.scalars().all()
    return [ReadingResponse.model_validate(r) for r in readings]

