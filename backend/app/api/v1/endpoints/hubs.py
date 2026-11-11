from typing import List, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.v1.deps import get_current_user, require_admin
from app.models.user import User
from app.schemas.hub import HubResponse, HubCreate
from app.services import hub_service

router = APIRouter()


@router.get("/", response_model=List[HubResponse])
async def list_hubs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    return await hub_service.get_all_hubs(db)


@router.get("/{hub_id}", response_model=HubResponse)
async def get_hub(
    hub_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    hub = await hub_service.get_hub_by_id(db, hub_id)
    if not hub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hub with ID {hub_id} not found."
        )
    return hub


@router.post("/", response_model=HubResponse, status_code=status.HTTP_201_CREATED)
async def create_new_hub(
    hub_in: HubCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(require_admin)
) -> Any:
    hub = await hub_service.create_hub(db, hub_in)
    return await hub_service.get_hub_by_id(db, hub.id)

