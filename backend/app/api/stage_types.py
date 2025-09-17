from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from starlette.concurrency import run_in_threadpool

from ..api.dependencies import get_db, get_current_actor_factory
from ..models.user import User
from ..schemas.stage_type import StageTypeRead, StageTypeCreate, StageTypeUpdate, PaginatedStageTypes
from ..services.stage_type_service import StageTypeService

router = APIRouter()

@router.get("", response_model=PaginatedStageTypes)
async def get_stage_types(
    db: Session = Depends(get_db),
    actor = Depends(get_current_actor_factory()),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_by: str = Query("name"),
    order_dir: str = Query("asc", pattern="^(asc|desc)$"),
    name: str = Query(None),
    is_active: bool = Query(None),
):
    service = StageTypeService(db)
    return await run_in_threadpool(
        service.get_stage_types,
        actor, limit, offset, order_by, order_dir, name, is_active
    )

@router.get("/active", response_model=List[StageTypeRead])
async def get_active_stage_types(
    db: Session = Depends(get_db),
    actor = Depends(get_current_actor_factory())
):
    service = StageTypeService(db)
    return await run_in_threadpool(service.get_active_stage_types, actor)

@router.get("/{stage_type_id}", response_model=StageTypeRead)
async def get_stage_type(
    stage_type_id: str,
    db: Session = Depends(get_db),
    actor = Depends(get_current_actor_factory())
):
    service = StageTypeService(db)
    return await run_in_threadpool(service.get_stage_type, stage_type_id, actor)

@router.post("", response_model=StageTypeRead)
async def create_stage_type(
    stage_type_data: StageTypeCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_actor_factory(["admin"]))
):
    service = StageTypeService(db)
    return await run_in_threadpool(service.create_stage_type, stage_type_data, admin_user)

@router.put("/{stage_type_id}", response_model=StageTypeRead)
async def update_stage_type(
    stage_type_id: str,
    stage_type_data: StageTypeUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_actor_factory(["admin"]))
):
    service = StageTypeService(db)
    return await run_in_threadpool(service.update_stage_type, stage_type_id, stage_type_data, admin_user)

@router.delete("/{stage_type_id}")
async def delete_stage_type(
    stage_type_id: str,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_actor_factory(["admin"]))
):
    service = StageTypeService(db)
    return await run_in_threadpool(service.delete_stage_type, stage_type_id, admin_user)
