import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Uuid
from sqlalchemy.orm import relationship

from app.core.database import Base


class Batch(Base):
    __tablename__ = "batches"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hub_id = Column(Uuid(as_uuid=True), ForeignKey("hubs.id", ondelete="CASCADE"), nullable=False, index=True)
    crop_type = Column(String(50), nullable=False)  # "moringa" | "prunus" | "hibiscus"
    initial_weight_kg = Column(Float, nullable=False)
    target_moisture_pct = Column(Float, nullable=False)
    status = Column(String(20), nullable=False, default="active", index=True)  # "active" | "completed"
    start_time = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    created_by_user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Latest snapshot predictions & advisory cache
    predicted_remaining_hours = Column(Float, nullable=True)
    predicted_quality_grade = Column(String(20), nullable=True)  # "export" | "standard" | "downgraded"
    latest_advisory = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    hub = relationship("Hub", back_populates="batches")
    created_by = relationship("User", back_populates="created_batches")
    readings = relationship("Reading", back_populates="batch", cascade="all, delete-orphan", order_by="Reading.timestamp.desc()")
    alerts = relationship("Alert", back_populates="batch", cascade="all, delete-orphan")

