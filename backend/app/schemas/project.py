from typing import Optional, List
from uuid import UUID
from datetime import datetime, date
from pydantic import BaseModel
import enum

class ProjectStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    paused = "paused"
    completed = "completed"
    cancelled = "cancelled"

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    total_value: float
    currency: str = "BRL"
    start_date: date
    estimated_end_date: date
    actual_end_date: Optional[date] = None
    status: ProjectStatus = ProjectStatus.draft
    work_address: Optional[dict] = None
    scope: Optional[dict] = None
    notes: Optional[str] = None

class ProjectCreate(ProjectBase):
    clients: List[UUID]

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    total_value: Optional[float] = None
    currency: Optional[str] = None
    start_date: Optional[date] = None
    estimated_end_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    status: Optional[ProjectStatus] = None
    work_address: Optional[dict] = None
    scope: Optional[dict] = None
    notes: Optional[str] = None
    clients: Optional[List[UUID]] = None

class ProjectRead(ProjectBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by_id: UUID
    clients: List[UUID]
    stages: Optional[List[UUID]] = None
    files: Optional[List[UUID]] = None

    class Config:
        from_attributes = True
