from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.batch import Batch
from app.models.hub import Hub
from app.models.reading import Reading
from app.models.user import User
from app.schemas.batch import BatchCreate, BatchResponse, BatchStatus, CropType, DEFAULT_TARGET_MOISTURE


async def create_batch(
    db: AsyncSession,
    batch_in: BatchCreate,
    current_user: User
) -> BatchResponse:
    # 1. Fetch Hub and verify existence
    hub = await db.get(Hub, batch_in.hub_id)
    if not hub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hub with ID {batch_in.hub_id} not found."
        )

    # 2. Operator hub scoping check
    if current_user.role == "operator" and current_user.hub_id != hub.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operators can only create batches for their assigned hub."
        )

    # 3. ADR-0002 Capacity Check: sum(active batch weights) + new_weight <= dryer_capacity_kg
    load_query = select(
        func.coalesce(func.sum(Batch.initial_weight_kg), 0.0)
    ).where(Batch.hub_id == hub.id, Batch.status == BatchStatus.ACTIVE.value)
    
    current_load_res = await db.execute(load_query)
    current_load = float(current_load_res.scalar() or 0.0)
    
    available_capacity = hub.dryer_capacity_kg - current_load
    if batch_in.initial_weight_kg > available_capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Dryer capacity exceeded for hub '{hub.name}'. "
                f"Total capacity: {hub.dryer_capacity_kg} kg, "
                f"current active load: {current_load:.1f} kg, "
                f"available: {available_capacity:.1f} kg. "
                f"Requested new batch weight: {batch_in.initial_weight_kg:.1f} kg."
            )
        )

    # 4. Set target moisture default if not specified
    target_moisture = batch_in.target_moisture_pct
    if target_moisture is None:
        target_moisture = DEFAULT_TARGET_MOISTURE.get(batch_in.crop_type, 11.0)

    # 5. Create Batch
    now = datetime.now(timezone.utc)
    new_batch = Batch(
        hub_id=hub.id,
        crop_type=batch_in.crop_type.value,
        initial_weight_kg=batch_in.initial_weight_kg,
        target_moisture_pct=target_moisture,
        status=BatchStatus.ACTIVE.value,
        start_time=now,
        created_by_user_id=current_user.id,
        latest_advisory=None
    )
    
    db.add(new_batch)
    await db.commit()
    await db.refresh(new_batch)

    return BatchResponse.model_validate(new_batch)


async def get_batches(
    db: AsyncSession,
    hub_id: Optional[UUID] = None,
    status_filter: Optional[BatchStatus] = None,
    crop_type: Optional[CropType] = None
) -> List[BatchResponse]:
    query = select(Batch).order_by(Batch.start_time.desc())
    
    if hub_id:
        query = query.where(Batch.hub_id == hub_id)
    if status_filter:
        query = query.where(Batch.status == status_filter.value)
    if crop_type:
        query = query.where(Batch.crop_type == crop_type.value)

    result = await db.execute(query)
    batches = result.scalars().all()

    responses = []
    for b in batches:
        # Fetch latest reading to populate current_moisture
        reading_q = select(Reading.current_moisture).where(
            Reading.batch_id == b.id
        ).order_by(Reading.timestamp.desc()).limit(1)
        r_res = await db.execute(reading_q)
        current_moist = r_res.scalar_one_or_none()

        resp = BatchResponse.model_validate(b)
        resp.current_moisture = current_moist
        responses.append(resp)

    return responses


async def get_batch_by_id(db: AsyncSession, batch_id: UUID) -> Optional[BatchResponse]:
    batch = await db.get(Batch, batch_id)
    if not batch:
        return None

    reading_q = select(Reading.current_moisture).where(
        Reading.batch_id == batch.id
    ).order_by(Reading.timestamp.desc()).limit(1)
    r_res = await db.execute(reading_q)
    current_moist = r_res.scalar_one_or_none()

    resp = BatchResponse.model_validate(batch)
    resp.current_moisture = current_moist
    return resp


async def complete_batch(
    db: AsyncSession,
    batch_id: UUID,
    current_user: User
) -> BatchResponse:
    batch = await db.get(Batch, batch_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch with ID {batch_id} not found."
        )

    if current_user.role == "operator" and current_user.hub_id != batch.hub_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operators can only manage batches at their assigned hub."
        )

    if batch.status == BatchStatus.COMPLETED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch is already completed."
        )

    batch.status = BatchStatus.COMPLETED.value
    batch.end_time = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(batch)

    return await get_batch_by_id(db, batch.id)

