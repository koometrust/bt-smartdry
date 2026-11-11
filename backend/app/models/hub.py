import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Uuid
from sqlalchemy.orm import relationship

from app.core.database import Base


class Hub(Base):
    __tablename__ = "hubs"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    location = Column(String(255), nullable=False)
    dryer_capacity_kg = Column(Float, nullable=False, default=200.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    users = relationship("User", back_populates="hub", cascade="all, delete-orphan")
    batches = relationship("Batch", back_populates="hub", cascade="all, delete-orphan")
