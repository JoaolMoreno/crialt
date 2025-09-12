from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
import enum

class FileCategory(str, enum.Enum):
    document = 'document'
    image = 'image'
    plan = 'plan'
    render = 'render'
    contract = 'contract'

class FileBase(BaseModel):
    original_name: str
    stored_name: str
    path: str
    size: int
    mime_type: str
    category: FileCategory
    description: Optional[str] = None

class FileCreate(FileBase):
    project_id: Optional[UUID] = None
    client_id: Optional[UUID] = None
    stage_id: Optional[UUID] = None
    uploaded_by_id: UUID

class FileUpdate(BaseModel):
    description: Optional[str] = None

class FileRead(FileBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    project_id: Optional[UUID] = None
    client_id: Optional[UUID] = None
    stage_id: Optional[UUID] = None
    uploaded_by_id: UUID

    class Config:
        from_attributes = True

class PaginatedFiles(BaseModel):
    total: int
    count: int
    offset: int
    limit: int
    items: List[FileRead]
