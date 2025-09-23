from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from datetime import datetime, timezone

from .base import Base


class ChunkedUpload(Base):
    __tablename__ = "chunked_uploads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    upload_id = Column(String(255), unique=True, nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    total_chunks = Column(Integer, nullable=False)
    chunk_size = Column(Integer, nullable=False)
    total_size = Column(Integer, nullable=False)
    file_checksum = Column(String(64))
    mime_type = Column(String(255))

    category = Column(String(50))
    project_id = Column(UUID(as_uuid=True))
    client_id = Column(UUID(as_uuid=True))
    stage_id = Column(UUID(as_uuid=True))
    description = Column(Text)
    uploaded_by_id = Column(UUID(as_uuid=True), nullable=False)

    uploaded_chunks = Column(Text, default="")
    is_completed = Column(Boolean, default=False)
    final_file_id = Column(UUID(as_uuid=True))

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True))
