from sqlalchemy import Column, String, Text, JSON, Integer, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from .base import Base


class StageType(Base):
    __tablename__ = "stage_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    scope = Column(JSON)
    default_duration_days = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    stages = relationship("Stage", back_populates="stage_type")

    def __repr__(self):
        return f"<StageType(id={self.id}, name='{self.name}')>"
