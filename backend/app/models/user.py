import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Boolean, DateTime, Enum as SQLAlchemyEnum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.schemas.user import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(SQLAlchemyEnum(UserRole), nullable=False, default=UserRole.architect)
    avatar = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    created_projects = relationship("Project", back_populates="created_by")
    created_stages = relationship("Stage", foreign_keys='[Stage.created_by_id]', back_populates="created_by")
    assigned_stages = relationship("Stage", foreign_keys='[Stage.assigned_to_id]', back_populates="assigned_to")
    uploaded_files = relationship("File", back_populates="uploaded_by")
    created_tasks = relationship("Task", foreign_keys='[Task.created_by_id]', back_populates="created_by")
    assigned_tasks = relationship("Task", foreign_keys='[Task.assigned_to_id]', back_populates="assigned_to")
