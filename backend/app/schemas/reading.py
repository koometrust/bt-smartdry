from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class ReadingBase(BaseModel):
    temperature: float = Field(..., description="Dryer internal temperature °C")
    humidity: float = Field(..., description="Dryer internal humidity %")
    vpd: float = Field(..., description="Vapour pressure deficit kPa")
    current_moisture: float = Field(..., description="Crop moisture content %")
    ambient_temperature: float = Field(..., description="External ambient temperature °C")
    ambient_humidity: float = Field(..., description="External ambient humidity %")


class ReadingCreate(ReadingBase):
    batch_id: UUID
    timestamp: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReadingResponse(ReadingBase):
    id: UUID
    batch_id: UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class ReadingBulkCreate(BaseModel):
    readings: List[ReadingCreate]

