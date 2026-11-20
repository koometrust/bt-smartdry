from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.models.hub import Hub
from app.models.batch import Batch

router = APIRouter()


@router.get("/overview")
async def get_analytics_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Returns network-wide or hub-scoped aggregated analytics, including
    total avoided post-harvest loss (kg) and economic value preserved (KES).
    """
    # Load all hubs
    hubs_res = await db.execute(select(Hub).order_by(Hub.name))
    hubs = hubs_res.scalars().all()
    hub_map = {h.id: h.name for h in hubs}

    # Load batches (Operators scoped to their hub if desired, but administrators see all)
    query = select(Batch)
    if current_user.role == "operator" and current_user.hub_id:
        query = query.where(Batch.hub_id == current_user.hub_id)

    batches_res = await db.execute(query)
    batches = batches_res.scalars().all()

    total_batches = len(batches)
    completed_batches = [b for b in batches if b.status == "completed"]
    active_batches = [b for b in batches if b.status == "active"]

    total_avoided_loss_kg = round(
        sum(b.avoided_loss_kg or 0.0 for b in completed_batches), 2
    )
    total_avoided_loss_kes = round(
        sum(b.avoided_loss_kes or 0.0 for b in completed_batches), 2
    )
    total_initial_weight_kg = round(
        sum(b.initial_weight_kg or 0.0 for b in batches), 2
    )

    # Crop breakdown
    crop_breakdown: Dict[str, Dict[str, Any]] = {}
    for crop in ["moringa", "prunus", "hibiscus"]:
        crop_batches = [b for b in batches if b.crop_type.lower() == crop]
        crop_completed = [b for b in crop_batches if b.status == "completed"]
        crop_breakdown[crop] = {
            "total_batches": len(crop_batches),
            "completed_batches": len(crop_completed),
            "total_weight_kg": round(sum(b.initial_weight_kg for b in crop_batches), 2),
            "avoided_loss_kg": round(sum(b.avoided_loss_kg or 0.0 for b in crop_completed), 2),
            "avoided_loss_kes": round(sum(b.avoided_loss_kes or 0.0 for b in crop_completed), 2),
        }

    # Hub breakdown
    hub_breakdown: List[Dict[str, Any]] = []
    for h in hubs:
        if current_user.role == "operator" and current_user.hub_id and h.id != current_user.hub_id:
            continue
        h_batches = [b for b in batches if b.hub_id == h.id]
        h_completed = [b for b in h_batches if b.status == "completed"]
        hub_breakdown.append({
            "hub_id": str(h.id),
            "hub_name": h.name,
            "total_batches": len(h_batches),
            "completed_batches": len(h_completed),
            "total_weight_kg": round(sum(b.initial_weight_kg for b in h_batches), 2),
            "avoided_loss_kg": round(sum(b.avoided_loss_kg or 0.0 for b in h_completed), 2),
            "avoided_loss_kes": round(sum(b.avoided_loss_kes or 0.0 for b in h_completed), 2),
        })

    return {
        "total_batches": total_batches,
        "completed_batches": len(completed_batches),
        "active_batches": len(active_batches),
        "total_weight_kg": total_initial_weight_kg,
        "total_avoided_loss_kg": total_avoided_loss_kg,
        "total_avoided_loss_kes": total_avoided_loss_kes,
        "crop_breakdown": crop_breakdown,
        "hub_breakdown": hub_breakdown,
    }

