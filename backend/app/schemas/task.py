import enum
from datetime import datetime, date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class TaskStatus(str, enum.Enum):
    todo = 'todo'
    in_progress = 'in_progress'
    completed = 'completed'
    cancelled = 'cancelled'

class TaskPriority(str, enum.Enum):
    low = 'low'
    medium = 'medium'
    high = 'high'
    urgent = 'urgent'

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.todo
    priority: TaskPriority = TaskPriority.medium
    due_date: Optional[date] = None

class TaskCreate(TaskBase):
    stage_id: UUID
    created_by_id: UUID
    assigned_to_id: Optional[UUID] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[date] = None
    assigned_to_id: Optional[UUID] = None

class TaskRead(TaskBase):
    id: UUID
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    stage_id: UUID
    created_by_id: UUID
    assigned_to_id: Optional[UUID] = None

    class Config:
        from_attributes = True
