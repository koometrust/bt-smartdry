import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Float, DateTime, ForeignKey, Uuid
from sqlalchemy.orm import relationship

from app.core.database import Base


class Reading(Base):
    __tablename__ = "readings"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id = Column(Uuid(as_uuid=True), ForeignKey("batches.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    
    # Sensor telemetry per batch (ambient fields duplicated per ADR-0002)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    vpd = Column(Float, nullable=False)
    current_moisture = Column(Float, nullable=False)
    ambient_temperature = Column(Float, nullable=False)
    ambient_humidity = Column(Float, nullable=False)

    batch = relationship("Batch", back_populates="readings")

