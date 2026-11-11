from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class HubBase(BaseModel):
    name: str = Field(..., max_length=100, description="Hub name (Meru, Tharaka Nithi, Eldoret)")
    location: str = Field(..., max_length=255)
    dryer_capacity_kg: float = Field(default=200.0, gt=0, description="Dryer capacity in kg")


class HubCreate(HubBase):
    pass


class HubResponse(HubBase):
    id: UUID
    created_at: datetime
    active_batch_count: int = 0
    current_load_kg: float = 0.0
    capacity_utilization_pct: float = 0.0

    model_config = ConfigDict(from_attributes=True)

