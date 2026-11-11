import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Uuid, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id = Column(Uuid(as_uuid=True), ForeignKey("batches.id", ondelete="CASCADE"), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)  # "near_completion" | "completion" | "anomaly"
    channel = Column(String(20), nullable=False, default="sms")
    message = Column(Text, nullable=False)
    phone_number = Column(String(30), nullable=False)
    status = Column(String(20), nullable=False, default="sent")  # "sent" | "failed"
    sent_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    batch = relationship("Batch", back_populates="alerts")

    __table_args__ = (
        UniqueConstraint("batch_id", "alert_type", name="uq_batch_alert_type"),
    )

