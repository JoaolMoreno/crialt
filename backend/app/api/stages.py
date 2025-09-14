from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..api.dependencies import get_db, get_current_actor_factory, client_resource_permission
from ..models.project import Project
from ..models.stage import Stage
from ..schemas.stage import StageRead, StageCreate, StageUpdate, PaginatedStages
from ..utils.cache import cache

router = APIRouter()

@router.get("", response_model=PaginatedStages)
def get_stages(
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_actor_factory(["admin"])),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_by: str = Query("created_at"),
    order_dir: str = Query("desc", pattern="^(asc|desc)$"),
    name: str = Query(None),
    type: str = Query(None),
    status: str = Query(None),
    project_id: str = Query(None),
    planned_start_date: str = Query(None),
):
    cache_params = {
        "limit": limit,
        "offset": offset,
        "order_by": order_by,
        "order_dir": order_dir,
        "name": name,
        "type": type,
        "status": status,
        "project_id": project_id,
        "planned_start_date": planned_start_date
    }
    cached = cache.get("stages", cache_params)
    if cached:
        return cached
    query = db.query(Stage)
    if name:
        query = query.filter(Stage.name.ilike(f"%{name}%"))
    if type:
        query = query.filter(Stage.type == type)
    if status:
        query = query.filter(Stage.status == status)
    if project_id:
        query = query.filter(Stage.project_id == project_id)
    if planned_start_date:
        query = query.filter(Stage.planned_start_date == planned_start_date)
    # Ordenação
    if hasattr(Stage, order_by):
        order_col = getattr(Stage, order_by)
        if order_dir == "desc":
            order_col = order_col.desc()
        else:
            order_col = order_col.asc()
        query = query.order_by(order_col)
    total = query.count()
    items = query.offset(offset).limit(limit).all()

    read_items = [StageRead.model_validate(item) for item in items]
    result = PaginatedStages(
        total=total,
        count=len(read_items),
        offset=offset,
        limit=limit,
        items=read_items
    )
    cache.set("stages", cache_params, result)
    return result

@router.get("/project/{project_id}", response_model=List[StageRead])
def get_stages_by_project(project_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor_factory())):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    client_ids = [str(client.id) for client in project.clients]
    client_resource_permission(client_ids, actor)
    stages = db.query(Stage).filter(Stage.project_id == project_id).all()
    return [StageRead.model_validate(stage) for stage in stages]
@router.get("/{stage_id}", response_model=StageRead)
def get_stage(stage_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor_factory())):
    stage = db.get(Stage, stage_id)
    if not stage:
        raise HTTPException(status_code=404, detail="Etapa não encontrada")
    project = db.get(Project, stage.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado para a etapa")
    client_ids = [str(client.id) for client in project.clients]
    client_resource_permission(client_ids, actor)
    return StageRead.model_validate(stage)

@router.post("", response_model=StageRead)
def create_stage(stage_data: StageCreate, db: Session = Depends(get_db), admin_user = Depends(get_current_actor_factory(["admin"]))):
    project = db.get(Project, stage_data.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    stage_dict = stage_data.model_dump()
    stage = Stage(**stage_dict)
    db.add(stage)
    db.commit()
    db.refresh(stage)
    cache.invalidate("stages")
    cache.invalidate("dashboard")
    return stage

@router.put("/{stage_id}", response_model=StageRead)
def update_stage(stage_id: str, stage_data: StageUpdate, db: Session = Depends(get_db), admin_user = Depends(get_current_actor_factory(["admin"]))):
    stage = db.get(Stage, stage_id)
    if not stage:
        raise HTTPException(status_code=404, detail="Etapa não encontrada")
    update_data = stage_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(stage, field, value)
    db.commit()
    db.refresh(stage)
    cache.invalidate("stages")
    cache.invalidate("dashboard")
    return stage

@router.delete("/{stage_id}")
def delete_stage(stage_id: str, db: Session = Depends(get_db), admin_user = Depends(get_current_actor_factory(["admin"]))):
    stage = db.get(Stage, stage_id)
    if not stage:
        raise HTTPException(status_code=404, detail="Etapa não encontrada")
    db.delete(stage)
    db.commit()
    cache.invalidate("stages")
    cache.invalidate("dashboard")
    return {"message": "Etapa removida com sucesso"}
