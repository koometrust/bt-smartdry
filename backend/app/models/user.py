import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Uuid
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="operator")  # "operator" | "admin"
    hub_id = Column(Uuid(as_uuid=True), ForeignKey("hubs.id", ondelete="SET NULL"), nullable=True)
    preferred_language = Column(String(10), nullable=False, default="en")  # "en" | "sw"
    phone_number = Column(String(30), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    hub = relationship("Hub", back_populates="users")
    created_batches = relationship("Batch", back_populates="created_by")

