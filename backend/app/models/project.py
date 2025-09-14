import uuid
from datetime import datetime, UTC

from sqlalchemy import (
    Column, String, DateTime, Date, Enum as SQLAlchemyEnum,
    JSON, ForeignKey, Numeric, Table
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..schemas.project import ProjectStatus
from ..models.base import Base
from .stage import Stage

project_clients = Table(
    'project_clients', Base.metadata,
    Column('project_id', UUID(as_uuid=True), ForeignKey('projects.id'), primary_key=True),
    Column('client_id', UUID(as_uuid=True), ForeignKey('clients.id'), primary_key=True)
)

class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    total_value = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="BRL", nullable=False)
    start_date = Column(Date, nullable=False, index=True)
    estimated_end_date = Column(Date, nullable=False)
    actual_end_date = Column(Date, nullable=True)
    status = Column(SQLAlchemyEnum(ProjectStatus), default=ProjectStatus.draft, nullable=False, index=True)
    work_address = Column(JSON, nullable=True)
    scope = Column(JSON, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    current_stage_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Relationships
    clients = relationship("Client", secondary=project_clients, back_populates="projects")
    stages = relationship("Stage", back_populates="project", cascade="all, delete-orphan", foreign_keys=[Stage.project_id])
    files = relationship("File", back_populates="project")
    created_by = relationship("User", back_populates="created_projects")
