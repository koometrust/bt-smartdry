from typing import List, Optional, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.schemas.batch import BatchCreate, BatchResponse, BatchStatus, CropType
from app.schemas.reading import ReadingResponse
from app.services import batch_service, reading_service

router = APIRouter()


@router.get("/", response_model=List[BatchResponse])
async def list_batches(
    hub_id: Optional[UUID] = None,
    status_filter: Optional[BatchStatus] = None,
    crop_type: Optional[CropType] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    # If operator, scope to their hub
    effective_hub_id = hub_id
    if current_user.role == "operator":
        effective_hub_id = current_user.hub_id

    return await batch_service.get_batches(
        db=db,
        hub_id=effective_hub_id,
        status_filter=status_filter,
        crop_type=crop_type
    )


@router.post("/", response_model=BatchResponse, status_code=status.HTTP_201_CREATED)
async def create_batch(
    batch_in: BatchCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    return await batch_service.create_batch(db, batch_in, current_user)


@router.get("/{batch_id}", response_model=BatchResponse)
async def get_batch(
    batch_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    batch = await batch_service.get_batch_by_id(db, batch_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch with ID {batch_id} not found."
        )
    if current_user.role == "operator" and current_user.hub_id != batch.hub_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operators can only access batches from their assigned hub."
        )
    return batch


@router.post("/{batch_id}/complete", response_model=BatchResponse)
async def complete_batch_action(
    batch_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    return await batch_service.complete_batch(db, batch_id, current_user)


@router.get("/{batch_id}/readings", response_model=List[ReadingResponse])
async def get_batch_readings_list(
    batch_id: UUID,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    batch = await batch_service.get_batch_by_id(db, batch_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch with ID {batch_id} not found."
        )
    return await reading_service.get_batch_readings(db, batch_id, limit=limit)

