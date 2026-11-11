from typing import List, Optional, Any
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.models.alert import Alert
from app.schemas.alert import AlertResponse

router = APIRouter()


@router.get("/", response_model=List[AlertResponse])
async def list_alerts(
    batch_id: Optional[UUID] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    query = select(Alert).order_by(Alert.sent_at.desc()).limit(limit)
    if batch_id:
        query = query.where(Alert.batch_id == batch_id)

    result = await db.execute(query)
    alerts = result.scalars().all()
    return [AlertResponse.model_validate(a) for a in alerts]

