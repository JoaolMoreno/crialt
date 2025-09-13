from typing import Optional, List
from uuid import UUID
from datetime import datetime, date
from pydantic import BaseModel
import enum

class StageStatus(str, enum.Enum):
    pending = 'pending'
    in_progress = 'in_progress'
    completed = 'completed'
    cancelled = 'cancelled'
    on_hold = 'on_hold'

class PaymentStatus(str, enum.Enum):
    pending = 'pending'
    partial = 'partial'
    paid = 'paid'

class StageBase(BaseModel):
    name: str
    description: Optional[str] = None
    order: int
    status: StageStatus = StageStatus.pending
    planned_start_date: date
    actual_start_date: Optional[date] = None
    planned_end_date: date
    actual_end_date: Optional[date] = None
    value: float
    payment_status: PaymentStatus = PaymentStatus.pending
    specific_data: Optional[dict] = None
    progress_percentage: int = 0
    notes: Optional[str] = None

class StageCreate(StageBase):
    project_id: UUID
    stage_type_id: UUID
    created_by_id: UUID
    assigned_to_id: Optional[UUID] = None

class StageUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None
    status: Optional[StageStatus] = None
    planned_start_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    value: Optional[float] = None
    payment_status: Optional[PaymentStatus] = None
    specific_data: Optional[dict] = None
    progress_percentage: Optional[int] = None
    notes: Optional[str] = None
    stage_type_id: Optional[UUID] = None
    assigned_to_id: Optional[UUID] = None

class StageRead(StageBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    project_id: UUID
    stage_type_id: UUID
    created_by_id: UUID
    assigned_to_id: Optional[UUID] = None
    files: Optional[List[UUID]] = None
    tasks: Optional[List[UUID]] = None

    stage_type: Optional[dict] = None

    class Config:
        from_attributes = True

class PaginatedStages(BaseModel):
    total: int
    count: int
    offset: int
    limit: int
    items: List[StageRead]
