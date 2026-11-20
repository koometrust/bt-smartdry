from typing import List, Optional, Any, Dict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.models.alert import Alert
from app.models.batch import Batch
from app.schemas.alert import AlertResponse

router = APIRouter()


@router.get("/", response_model=List[AlertResponse])
async def list_alerts(
    batch_id: Optional[UUID] = None,
    hub_id: Optional[UUID] = None,
    alert_type: Optional[str] = None,
    limit: int = 50,
    skip: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    List alerts with role-based scoping and query filters.
    Operators can only access alerts for batches at their assigned hub.
    Administrators have network-wide visibility.
    """
    query = select(Alert).join(Batch, Alert.batch_id == Batch.id).order_by(Alert.sent_at.desc())

    # Role scoping
    if current_user.role == "operator":
        if hub_id and hub_id != current_user.hub_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operators can only access alerts from their assigned hub."
            )
        query = query.where(Batch.hub_id == current_user.hub_id)
    elif hub_id:
        query = query.where(Batch.hub_id == hub_id)

    if batch_id:
        query = query.where(Alert.batch_id == batch_id)

    if alert_type:
        query = query.where(Alert.alert_type == alert_type.lower())

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    alerts = result.scalars().all()
    return [AlertResponse.model_validate(a) for a in alerts]


@router.get("/unread-count")
async def get_unread_alerts_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, int]:
    """
    Returns the count of unread alerts within the authenticated user's scope.
    """
    query = (
        select(func.count(Alert.id))
        .join(Batch, Alert.batch_id == Batch.id)
        .where(Alert.is_read == False)
    )

    if current_user.role == "operator":
        query = query.where(Batch.hub_id == current_user.hub_id)

    res = await db.execute(query)
    count = res.scalar_one() or 0
    return {"unread_count": count}


@router.post("/{alert_id}/read", response_model=AlertResponse)
async def mark_alert_as_read(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Marks an alert as read/acknowledged.
    """
    query = select(Alert).where(Alert.id == alert_id).options(selectinload(Alert.batch))
    res = await db.execute(query)
    alert = res.scalar_one_or_none()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found."
        )

    if current_user.role == "operator":
        if alert.batch and alert.batch.hub_id != current_user.hub_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operators can only modify alerts for their assigned hub."
            )

    alert.is_read = True
    await db.commit()
    await db.refresh(alert)

    return AlertResponse.model_validate(alert)
