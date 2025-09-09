import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, DateTime, Enum as SQLAlchemyEnum,
    ForeignKey, Integer
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.schemas.file import FileCategory
from app.models.base import Base

class File(Base):
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_name = Column(String, nullable=False)
    stored_name = Column(String, nullable=False, unique=True)
    path = Column(String, nullable=False)
    size = Column(Integer, nullable=False)  # size in bytes
    mime_type = Column(String, nullable=False)
    category = Column(SQLAlchemyEnum(FileCategory), nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign Keys
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=True)
    stage_id = Column(UUID(as_uuid=True), ForeignKey("stages.id"), nullable=True)
    uploaded_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="files")
    client = relationship("Client", back_populates="documents")
    stage = relationship("Stage", back_populates="files")
    uploaded_by = relationship("User", back_populates="uploaded_files")

