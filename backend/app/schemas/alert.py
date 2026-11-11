from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class AlertType(str, Enum):
    NEAR_COMPLETION = "near_completion"
    COMPLETION = "completion"
    ANOMALY = "anomaly"


class AlertChannel(str, Enum):
    SMS = "sms"


class AlertStatus(str, Enum):
    SENT = "sent"
    FAILED = "failed"


class AlertCreate(BaseModel):
    batch_id: UUID
    alert_type: AlertType
    channel: AlertChannel = AlertChannel.SMS
    message: str
    phone_number: str
    status: AlertStatus = AlertStatus.SENT


class AlertResponse(BaseModel):
    id: UUID
    batch_id: UUID
    alert_type: AlertType
    channel: AlertChannel
    message: str
    phone_number: str
    status: AlertStatus
    sent_at: datetime

    model_config = ConfigDict(from_attributes=True)

