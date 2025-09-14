import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, DateTime, Date, Enum as SQLAlchemyEnum,
    JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..schemas.client import DocumentType
from ..models.base import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    document = Column(String, unique=True, index=True, nullable=False)
    document_type = Column(SQLAlchemyEnum(DocumentType), nullable=False)
    rg_ie = Column(String, nullable=True)
    birth_date = Column(Date, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    secondary_email = Column(String, nullable=True)
    phone = Column(String, nullable=False)
    mobile = Column(String, nullable=True)
    whatsapp = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)
    first_access = Column(Boolean, default=True)
    address = Column(JSON, nullable=True)
    notes = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    projects = relationship("Project", secondary="project_clients", back_populates="clients")
    documents = relationship("File", back_populates="client")
