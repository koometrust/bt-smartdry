from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hub import Hub
from app.models.batch import Batch
from app.schemas.hub import HubResponse, HubCreate


async def get_all_hubs(db: AsyncSession) -> List[HubResponse]:
    query = select(Hub)
    result = await db.execute(query)
    hubs = result.scalars().all()
    
    responses = []
    for hub in hubs:
        # Calculate active load
        load_query = select(
            func.count(Batch.id).label("count"),
            func.coalesce(func.sum(Batch.initial_weight_kg), 0.0).label("total_weight")
        ).where(Batch.hub_id == hub.id, Batch.status == "active")
        
        load_res = await db.execute(load_query)
        count, total_weight = load_res.one()
        
        utilization = (total_weight / hub.dryer_capacity_kg) * 100.0 if hub.dryer_capacity_kg > 0 else 0.0
        
        responses.append(HubResponse(
            id=hub.id,
            name=hub.name,
            location=hub.location,
            dryer_capacity_kg=hub.dryer_capacity_kg,
            created_at=hub.created_at,
            active_batch_count=count,
            current_load_kg=round(total_weight, 2),
            capacity_utilization_pct=round(utilization, 1)
        ))
    return responses


async def get_hub_by_id(db: AsyncSession, hub_id: UUID) -> Optional[HubResponse]:
    hub = await db.get(Hub, hub_id)
    if not hub:
        return None
        
    load_query = select(
        func.count(Batch.id).label("count"),
        func.coalesce(func.sum(Batch.initial_weight_kg), 0.0).label("total_weight")
    ).where(Batch.hub_id == hub.id, Batch.status == "active")
    
    load_res = await db.execute(load_query)
    count, total_weight = load_res.one()
    utilization = (total_weight / hub.dryer_capacity_kg) * 100.0 if hub.dryer_capacity_kg > 0 else 0.0
    
    return HubResponse(
        id=hub.id,
        name=hub.name,
        location=hub.location,
        dryer_capacity_kg=hub.dryer_capacity_kg,
        created_at=hub.created_at,
        active_batch_count=count,
        current_load_kg=round(total_weight, 2),
        capacity_utilization_pct=round(utilization, 1)
    )


async def create_hub(db: AsyncSession, hub_in: HubCreate) -> Hub:
    hub = Hub(
        name=hub_in.name,
        location=hub_in.location,
        dryer_capacity_kg=hub_in.dryer_capacity_kg
    )
    db.add(hub)
    await db.commit()
    await db.refresh(hub)
    return hub

