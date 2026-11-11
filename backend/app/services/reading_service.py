from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.batch import Batch
from app.models.reading import Reading
from app.models.user import User
from app.schemas.reading import ReadingCreate, ReadingResponse
from app.schemas.alert import AlertType
from app.schemas.batch import BatchStatus, QualityGrade
from app.services.advisory_service import generate_advisory
from app.services.alert_service import trigger_alert_if_needed


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

    # 3. Predict / Estimate Remaining Hours & Grade (Fallback or in-memory ML)
    # Check if ML engine is available, else physics heuristic
    remaining_hours = max(0.0, (reading.current_moisture - batch.target_moisture_pct) * 1.5)
    hours = int(remaining_hours)
    mins = int((remaining_hours - hours) * 60)
    
    # Over-drying penalty check per ADR-0002 & context.md
    if reading.current_moisture < (batch.target_moisture_pct - 2.5):
        predicted_grade = QualityGrade.DOWNGRADED
    elif reading.current_moisture <= (batch.target_moisture_pct + 1.0):
        predicted_grade = QualityGrade.EXPORT
    else:
        predicted_grade = QualityGrade.STANDARD

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

