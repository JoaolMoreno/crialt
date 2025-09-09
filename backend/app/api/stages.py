from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import get_db, get_current_actor, client_resource_permission, admin_required
from app.models.stage import Stage
from app.models.project import Project
from app.schemas.stage import StageRead, StageCreate, StageUpdate

router = APIRouter()

@router.get("/", response_model=List[StageRead])
def get_stages(db: Session = Depends(get_db), admin_user = Depends(admin_required)):
    stages = db.query(Stage).all()
    return stages

@router.get("/project/{project_id}", response_model=List[StageRead])
def get_stages_by_project(project_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    client_ids = [str(client.id) for client in project.clients]
    client_resource_permission(client_ids, actor)
    stages = db.query(Stage).filter(Stage.project_id == project_id).all()
    return stages

@router.get("/{stage_id}", response_model=StageRead)
def get_stage(stage_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor)):
    stage = db.get(Stage, stage_id)
    if not stage:
        raise HTTPException(status_code=404, detail="Etapa não encontrada")
    project = db.get(Project, stage.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado para a etapa")
    client_ids = [str(client.id) for client in project.clients]
    client_resource_permission(client_ids, actor)
    return stage

@router.post("/", response_model=StageRead)
def create_stage(stage_data: StageCreate, db: Session = Depends(get_db), admin_user = Depends(admin_required)):
    # Verificar se o projeto existe
    project = db.get(Project, stage_data.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    stage_dict = stage_data.model_dump()
    stage = Stage(**stage_dict)
    db.add(stage)
    db.commit()
    db.refresh(stage)
    return stage

@router.put("/{stage_id}", response_model=StageRead)
def update_stage(stage_id: str, stage_data: StageUpdate, db: Session = Depends(get_db), admin_user = Depends(admin_required)):
    stage = db.get(Stage, stage_id)
    if not stage:
        raise HTTPException(status_code=404, detail="Etapa não encontrada")

    update_data = stage_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(stage, field, value)

    db.commit()
    db.refresh(stage)
    return stage

@router.delete("/{stage_id}")
def delete_stage(stage_id: str, db: Session = Depends(get_db), admin_user = Depends(admin_required)):
    stage = db.get(Stage, stage_id)
    if not stage:
        raise HTTPException(status_code=404, detail="Etapa não encontrada")

    db.delete(stage)
    db.commit()
    return {"message": "Etapa removida com sucesso"}
