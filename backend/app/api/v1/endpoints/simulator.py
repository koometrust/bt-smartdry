from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.services.simulator_service import simulator_manager

router = APIRouter()


class SimulatorStartRequest(BaseModel):
    interval_seconds: float = Field(default=2.0, ge=0.1, le=60.0, description="Simulation interval in seconds")
    speedup: float = Field(default=0.35, ge=0.01, le=5.0, description="Virtual hours progressed per tick")


@router.post("/start")
async def start_simulator(
    payload: Optional[SimulatorStartRequest] = None,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Start the on-demand telemetry generator for active batches.
    Authorized for Operators and Administrators.
    """
    interval = payload.interval_seconds if payload else 2.0
    speedup = payload.speedup if payload else 0.35
    return await simulator_manager.start(interval_seconds=interval, speedup=speedup)


@router.post("/stop")
async def stop_simulator(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Stop the on-demand telemetry generator.
    Authorized for Operators and Administrators.
    """
    return await simulator_manager.stop()


@router.get("/status")
async def get_simulator_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Returns the real-time operational status of the on-demand simulator.
    """
    return await simulator_manager.get_status(db)

