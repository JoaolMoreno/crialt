from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from ..api.dependencies import get_db, get_current_actor_factory
from ..models.user import User
from ..schemas.stage_type import StageTypeRead, StageTypeCreate, StageTypeUpdate, PaginatedStageTypes
from ..services.stage_type_service import StageTypeService
from ..utils.cache import cache

router = APIRouter()

@router.get("", response_model=PaginatedStageTypes)
def get_stage_types(
    db: Session = Depends(get_db),
    actor = Depends(get_current_actor_factory()),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_by: str = Query("name"),
    order_dir: str = Query("asc", pattern="^(asc|desc)$"),
    name: str = Query(None),
    is_active: bool = Query(None),
):
    cache_params = {
        "limit": limit,
        "offset": offset,
        "order_by": order_by,
        "order_dir": order_dir,
        "name": name,
        "is_active": is_active
    }
    cached = cache.get("stage_types", cache_params)
    if cached:
        return cached

    service = StageTypeService(db)
    stage_types, total = service.get_stage_types(
        skip=offset,
        limit=limit,
        name=name,
        is_active=is_active
    )

    result = PaginatedStageTypes(
        total=total,
        count=len(stage_types),
        offset=offset,
        limit=limit,
        items=[StageTypeRead.model_validate(st) for st in stage_types]
    )

    cache.set("stage_types", cache_params, result)
    return result

@router.get("/active", response_model=List[StageTypeRead])
def get_active_stage_types(
    db: Session = Depends(get_db),
    actor = Depends(get_current_actor_factory())
):
    service = StageTypeService(db)
    stage_types = service.get_active_stage_types()
    return [StageTypeRead.model_validate(st) for st in stage_types]

@router.get("/{stage_type_id}", response_model=StageTypeRead)
def get_stage_type(
    stage_type_id: str,
    db: Session = Depends(get_db),
    actor = Depends(get_current_actor_factory())
):
    service = StageTypeService(db)
    stage_type = service.get_stage_type(stage_type_id)
    if not stage_type:
        raise HTTPException(status_code=404, detail="Tipo de etapa não encontrado")
    return StageTypeRead.model_validate(stage_type)

@router.post("", response_model=StageTypeRead)
def create_stage_type(
    stage_type_data: StageTypeCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_actor_factory(["admin"]))
):
    service = StageTypeService(db)

    if service.stage_type_exists(stage_type_data.name):
        raise HTTPException(
            status_code=400,
            detail="Já existe um tipo de etapa com este nome"
        )

    stage_type = service.create_stage_type(stage_type_data)
    cache.invalidate("stage_types")
    cache.invalidate("dashboard")

    return StageTypeRead.model_validate(stage_type)

@router.put("/{stage_type_id}", response_model=StageTypeRead)
def update_stage_type(
    stage_type_id: str,
    stage_type_data: StageTypeUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_actor_factory(["admin"]))
):
    service = StageTypeService(db)

    if stage_type_data.name and service.stage_type_exists(stage_type_data.name, stage_type_id):
        raise HTTPException(
            status_code=400,
            detail="Já existe um tipo de etapa com este nome"
        )

    stage_type = service.update_stage_type(stage_type_id, stage_type_data)
    if not stage_type:
        raise HTTPException(status_code=404, detail="Tipo de etapa não encontrado")

    cache.invalidate("stage_types")
    cache.invalidate("dashboard")

    return StageTypeRead.model_validate(stage_type)

@router.delete("/{stage_type_id}")
def delete_stage_type(
    stage_type_id: str,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_actor_factory(["admin"]))
):
    service = StageTypeService(db)
    success = service.delete_stage_type(stage_type_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tipo de etapa não encontrado")

    cache.invalidate("stage_types")
    cache.invalidate("dashboard")

    return {"message": "Tipo de etapa desativado com sucesso"}
