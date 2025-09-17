import enum
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel

from .client import ClientBasicRead

def serialize_project(project):
    stages = getattr(project, "stages", [])
    if stages:
        stages = sorted(stages, key=lambda s: s.order)

    return {
        "id": project.id,
        "name": project.name,
        "description": getattr(project, "description", None),
        "total_value": project.total_value,
        "currency": project.currency,
        "start_date": project.start_date,
        "estimated_end_date": project.estimated_end_date,
        "actual_end_date": getattr(project, "actual_end_date", None),
        "status": project.status,
        "work_address": getattr(project, "work_address", None),
        "scope": getattr(project, "scope", None),
        "notes": getattr(project, "notes", None),
        "created_at": project.created_at,
        "updated_at": project.updated_at,
        "created_by_id": project.created_by_id,
        "current_stage_id": project.current_stage_id,
        "clients": [ClientBasicRead.model_validate(c) for c in getattr(project, "clients", [])],
        "stages": [serialize_stage(s) for s in stages],
        "files": [FileRead.model_validate(f) for f in getattr(project, "files", [])] if hasattr(project, "files") else [],
    }

def serialize_stage(stage):
    stage_dict = {
        "id": stage.id,
        "name": stage.name,
        "description": stage.description,
        "order": stage.order,
        "status": stage.status,
        "planned_start_date": stage.planned_start_date,
        "actual_start_date": stage.actual_start_date,
        "planned_end_date": stage.planned_end_date,
        "actual_end_date": stage.actual_end_date,
        "value": stage.value,
        "payment_status": stage.payment_status,
        "specific_data": stage.specific_data,
        "progress_percentage": stage.progress_percentage,
        "notes": stage.notes,
        "created_at": stage.created_at,
        "updated_at": stage.updated_at,
        "project_id": stage.project_id,
        "stage_type_id": stage.stage_type_id,
        "created_by_id": stage.created_by_id,
        "assigned_to_id": stage.assigned_to_id,
        "files": getattr(stage, "files", []),
        "tasks": getattr(stage, "tasks", []),
        "stage_type": None
    }

    if hasattr(stage, "stage_type") and stage.stage_type:
        stage_dict["stage_type"] = {
            "id": str(stage.stage_type.id),
            "name": stage.stage_type.name,
            "description": stage.stage_type.description,
            "scope": stage.stage_type.scope,
            "default_duration_days": stage.stage_type.default_duration_days,
            "is_active": stage.stage_type.is_active,
            "created_at": stage.stage_type.created_at,
            "updated_at": stage.stage_type.updated_at
        }

    return StageRead.model_validate(stage_dict)


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
