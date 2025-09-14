import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, DateTime, Date, Enum as SQLAlchemyEnum,
    JSON, ForeignKey, Numeric, Integer
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..schemas.stage import StageStatus, PaymentStatus
from ..models.base import Base


class Stage(Base):
    __tablename__ = "stages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    order = Column(Integer, nullable=False)
    status = Column(SQLAlchemyEnum(StageStatus), default=StageStatus.pending, nullable=False)
    planned_start_date = Column(Date, nullable=False)
    actual_start_date = Column(Date, nullable=True)
    planned_end_date = Column(Date, nullable=False)
    actual_end_date = Column(Date, nullable=True)
    value = Column(Numeric(10, 2), nullable=False)
    payment_status = Column(SQLAlchemyEnum(PaymentStatus), default=PaymentStatus.pending, nullable=False)
    specific_data = Column(JSON, nullable=True)
    progress_percentage = Column(Integer, default=0)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    stage_type_id = Column(UUID(as_uuid=True), ForeignKey("stage_types.id"), nullable=False, index=True)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    project = relationship("Project", back_populates="stages")
    stage_type = relationship("StageType", back_populates="stages")
    files = relationship("File", back_populates="stage")
    tasks = relationship("Task", back_populates="stage", cascade="all, delete-orphan")
    created_by = relationship("User", foreign_keys=[created_by_id], back_populates="created_stages")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], back_populates="assigned_stages")
