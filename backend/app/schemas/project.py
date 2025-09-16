import enum
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel

from .client import ClientBasicRead


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


class StageCreateForProject(BaseModel):
    stage_type_id: UUID
    name: Optional[str] = None  # Se não fornecido, usará o nome do stage_type
    description: Optional[str] = None  # Se não fornecido, usará a descrição do stage_type
    order: int
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    value: Optional[float] = 0
    payment_status: Optional[str] = "pending"
    progress_percentage: Optional[int] = 0
    notes: Optional[str] = None


class StageUpdateForProject(BaseModel):
    id: Optional[UUID] = None  # Se fornecido, atualiza stage existente
    stage_type_id: UUID
    name: Optional[str] = None
    description: Optional[str] = None
    order: int
    status: Optional[str] = "pending"
    planned_start_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    value: Optional[float] = 0
    payment_status: Optional[str] = "pending"
    progress_percentage: Optional[int] = 0
    notes: Optional[str] = None
    assigned_to_id: Optional[UUID] = None


class ProjectCreate(ProjectBase):
    clients: List[UUID]
    stages: Optional[List[StageCreateForProject]] = None


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
    stages: Optional[List[StageUpdateForProject]] = None


class ProjectRead(ProjectBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by_id: UUID
    current_stage_id: Optional[UUID] = None
    clients: List[ClientBasicRead]
    stages: Optional[List["StageRead"]] = None
    files: Optional[List["FileRead"]] = None

    class Config:
        from_attributes = True

from .stage import StageRead
from .file import FileRead
from .client import ClientRead

ClientRead.model_rebuild()


class PaginatedProjects(BaseModel):
    total: int
    count: int
    offset: int
    limit: int
    items: List[ProjectRead]
