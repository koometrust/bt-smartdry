import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.batch import Batch
from app.models.hub import Hub
from app.schemas.reading import ReadingCreate
from app.services import reading_service
from app.services.physics import (
    simulate_ambient,
    simulate_dryer,
    next_moisture_level,
    HUB_CLIMATES,
)

logger = logging.getLogger(__name__)


class SimulatorManager:
    def __init__(self, session_factory=None):
        self.session_factory = session_factory
        self.is_running: bool = False
        self.interval_seconds: float = 2.0
        self.speedup_hours_per_tick: float = 0.35
        self.last_tick_at: Optional[datetime] = None
        self._task: Optional[asyncio.Task] = None
        self._batch_moisture: Dict[UUID, float] = {}

    async def get_status(self, db: AsyncSession) -> Dict[str, Any]:
        count_q = select(Batch).where(Batch.status == "active")
        res = await db.execute(count_q)
        active_batches = res.scalars().all()
        return {
            "is_running": self.is_running,
            "active_batches_count": len(active_batches),
            "last_tick_at": self.last_tick_at.isoformat() if self.last_tick_at else None,
            "interval_seconds": self.interval_seconds,
            "speedup_hours_per_tick": self.speedup_hours_per_tick,
        }

    async def start(
        self,
        interval_seconds: float = 2.0,
        speedup: float = 0.35
    ) -> Dict[str, Any]:
        if self.is_running:
            return {
                "is_running": True,
                "message": "Simulator is already actively running.",
                "interval_seconds": self.interval_seconds,
            }

        self.interval_seconds = max(0.1, interval_seconds)
        self.speedup_hours_per_tick = speedup
        self.is_running = True
        self._task = asyncio.create_task(self._simulation_loop())
        logger.info(f"On-demand simulator started (interval={self.interval_seconds}s, speedup={self.speedup_hours_per_tick}h/tick)")
        return {
            "is_running": True,
            "message": "Simulator started successfully.",
            "interval_seconds": self.interval_seconds,
            "speedup_hours_per_tick": self.speedup_hours_per_tick,
        }

    async def stop(self) -> Dict[str, Any]:
        if not self.is_running:
            return {"is_running": False, "message": "Simulator is already stopped."}

        self.is_running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._task = None
        logger.info("On-demand simulator stopped cleanly.")
        return {"is_running": False, "message": "Simulator stopped successfully."}

    async def _simulation_loop(self):
        try:
            while self.is_running:
                await self._step_simulation()
                await asyncio.sleep(self.interval_seconds)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in simulator loop: {e}", exc_info=True)
            self.is_running = False

    async def _step_simulation(self):
        factory = self.session_factory or AsyncSessionLocal
        async with factory() as session:
            now_dt = datetime.now(timezone.utc)
            hour_of_day = (now_dt.hour + now_dt.minute / 60.0) % 24.0

            # Query active batches
            query = select(Batch).where(Batch.status == "active")
            result = await session.execute(query)
            active_batches = result.scalars().all()

            if not active_batches:
                self.last_tick_at = now_dt
                return

            # Preload hubs
            hub_ids = list({b.hub_id for b in active_batches})
            hubs_q = select(Hub).where(Hub.id.in_(hub_ids))
            h_res = await session.execute(hubs_q)
            hubs_map = {h.id: h for h in h_res.scalars().all()}

            for batch in active_batches:
                hub = hubs_map.get(batch.hub_id)
                hub_loc = hub.location if hub else "Meru"

                # Current moisture tracking
                if batch.id not in self._batch_moisture:
                    from app.models.reading import Reading
                    r_q = (
                        select(Reading.current_moisture)
                        .where(Reading.batch_id == batch.id)
                        .order_by(Reading.timestamp.desc())
                        .limit(1)
                    )
                    r_res = await session.execute(r_q)
                    last_m = r_res.scalar_one_or_none()
                    self._batch_moisture[batch.id] = last_m if last_m is not None else 75.0

                curr_m = self._batch_moisture[batch.id]
                target_m = batch.target_moisture_pct

                # Halt ticks if already at target moisture
                if curr_m <= target_m:
                    continue

                amb_temp, amb_rh = simulate_ambient(hub_loc, hour_of_day)
                dryer_temp, dryer_rh, dryer_vpd = simulate_dryer(
                    hub_loc, amb_temp, amb_rh, hour_of_day, curr_m
                )

                new_m = next_moisture_level(
                    crop_type=batch.crop_type,
                    current_moisture=curr_m,
                    dryer_temp=dryer_temp,
                    dryer_vpd=dryer_vpd,
                    batch_weight_kg=batch.initial_weight_kg,
                    dt_hours=self.speedup_hours_per_tick
                )
                self._batch_moisture[batch.id] = new_m

                reading_in = ReadingCreate(
                    batch_id=batch.id,
                    temperature=dryer_temp,
                    humidity=dryer_rh,
                    vpd=dryer_vpd,
                    current_moisture=new_m,
                    ambient_temperature=amb_temp,
                    ambient_humidity=amb_rh,
                    timestamp=now_dt
                )
                try:
                    await reading_service.create_reading(session, reading_in)
                except Exception as ex:
                    logger.warning(f"Failed to record reading for batch {batch.id}: {ex}")

            self.last_tick_at = now_dt


simulator_manager = SimulatorManager()
