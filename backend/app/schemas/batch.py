from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class CropType(str, Enum):
    MORINGA = "moringa"
    PRUNUS = "prunus"
    HIBISCUS = "hibiscus"


class BatchStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"


class QualityGrade(str, Enum):
    EXPORT = "export"
    STANDARD = "standard"
    DOWNGRADED = "downgraded"


DEFAULT_TARGET_MOISTURE = {
    CropType.MORINGA: 10.0,
    CropType.PRUNUS: 12.0,
    CropType.HIBISCUS: 11.0,
}


class BatchCreate(BaseModel):
    hub_id: UUID
    crop_type: CropType
    initial_weight_kg: float = Field(..., gt=0, le=200.0, description="Batch weight in kg (Dryer max 200 kg)")
    target_moisture_pct: Optional[float] = Field(default=None, description="Target moisture %; defaults per crop if omitted")


class BatchResponse(BaseModel):
    id: UUID
    hub_id: UUID
    crop_type: CropType
    initial_weight_kg: float
    target_moisture_pct: float
    status: BatchStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    created_by_user_id: Optional[UUID] = None
    
    # Real-time state & cached predictions
    current_moisture: Optional[float] = None
    predicted_remaining_hours: Optional[float] = None
    predicted_quality_grade: Optional[QualityGrade] = None
    latest_advisory: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BatchCompleteRequest(BaseModel):
    final_notes: Optional[str] = None

