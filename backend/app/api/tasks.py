from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..api.dependencies import get_db, get_current_actor_factory, client_resource_permission
from ..models.task import Task
from ..models.stage import Stage
from ..models.project import Project
from ..schemas.task import TaskRead, TaskCreate, TaskUpdate

router = APIRouter()

@router.get("/", response_model=List[TaskRead])
def get_tasks(db: Session = Depends(get_db), admin_user = Depends(get_current_actor_factory(["admin"]))):
    tasks = db.query(Task).all()
    return tasks

@router.get("/stage/{stage_id}", response_model=List[TaskRead])
def get_tasks_by_stage(stage_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor_factory())):
    # Buscar a etapa e verificar permissão através do projeto
    stage = db.get(Stage, stage_id)
    if not stage:
        raise HTTPException(status_code=404, detail="Etapa não encontrada")
    project = db.get(Project, stage.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado para a etapa")
    client_ids = [str(client.id) for client in project.clients]
    client_resource_permission(client_ids, actor)
    tasks = db.query(Task).filter(Task.stage_id == stage_id).all()
    return tasks

@router.get("/project/{project_id}", response_model=List[TaskRead])
def get_tasks_by_project(project_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor_factory())):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    client_ids = [str(client.id) for client in project.clients]
    client_resource_permission(client_ids, actor)
    # Buscar todas as tasks das stages deste projeto
    tasks = db.query(Task).join(Stage).filter(Stage.project_id == project_id).all()
    return tasks

@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor_factory())):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    stage = db.get(Stage, task.stage_id)
    if not stage:
        raise HTTPException(status_code=404, detail="Etapa não encontrada para a tarefa")
    project = db.get(Project, stage.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado para a tarefa")
    client_ids = [str(client.id) for client in project.clients]
    client_resource_permission(client_ids, actor)
    return task

@router.post("/", response_model=TaskRead)
def create_task(task_data: TaskCreate, db: Session = Depends(get_db), admin_user = Depends(get_current_actor_factory(["admin"]))):
    # Verificar se a etapa existe
    stage = db.get(Stage, task_data.stage_id)
    if not stage:
        raise HTTPException(status_code=404, detail="Etapa não encontrada")

    task_dict = task_data.model_dump()
    task = Task(**task_dict)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.put("/{task_id}", response_model=TaskRead)
def update_task(task_id: str, task_data: TaskUpdate, db: Session = Depends(get_db), admin_user = Depends(get_current_actor_factory(["admin"]))):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db), admin_user = Depends(get_current_actor_factory(["admin"]))):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    db.delete(task)
    db.commit()
    return {"message": "Tarefa removida com sucesso"}
