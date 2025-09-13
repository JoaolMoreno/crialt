from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..api.dependencies import get_db, get_current_actor_factory, client_resource_permission
from ..models.project import Project
from ..models.stage import Stage
from ..models.task import Task
from ..schemas.task import TaskRead, TaskCreate, TaskUpdate, PaginatedTasks
from ..utils.cache import cache

router = APIRouter()

@router.get("", response_model=PaginatedTasks)
def get_tasks(
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_actor_factory(["admin"])),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_by: str = Query("created_at"),
    order_dir: str = Query("desc", pattern="^(asc|desc)$"),
    title: str = Query(None),
    status: str = Query(None),
    priority: str = Query(None),
    due_date: str = Query(None),
    stage_id: str = Query(None),
    created_by_id: str = Query(None),
    assigned_to_id: str = Query(None),
):
    cache_params = {
        "limit": limit,
        "offset": offset,
        "order_by": order_by,
        "order_dir": order_dir,
        "title": title,
        "status": status,
        "priority": priority,
        "due_date": due_date,
        "stage_id": stage_id,
        "created_by_id": created_by_id,
        "assigned_to_id": assigned_to_id
    }
    cached = cache.get("tasks", cache_params)
    if cached:
        return cached
    query = db.query(Task)
    if title:
        query = query.filter(Task.title.ilike(f"%{title}%"))
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if due_date:
        query = query.filter(Task.due_date == due_date)
    if stage_id:
        query = query.filter(Task.stage_id == stage_id)
    if created_by_id:
        query = query.filter(Task.created_by_id == created_by_id)
    if assigned_to_id:
        query = query.filter(Task.assigned_to_id == assigned_to_id)
    # Ordenação
    if hasattr(Task, order_by):
        order_col = getattr(Task, order_by)
        if order_dir == "desc":
            order_col = order_col.desc()
        else:
            order_col = order_col.asc()
        query = query.order_by(order_col)
    total = query.count()
    items = query.offset(offset).limit(limit).all()
    result = PaginatedTasks(
        total=total,
        count=len(items),
        offset=offset,
        limit=limit,
        items=items
    )
    cache.set("tasks", cache_params, result)
    return result

@router.get("/stage/{stage_id}", response_model=List[TaskRead])
def get_tasks_by_stage(stage_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor_factory())):
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

@router.post("", response_model=TaskRead)
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
    cache.invalidate("tasks")
    cache.invalidate("dashboard")
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
    cache.invalidate("tasks")
    cache.invalidate("dashboard")
    return task

@router.delete("/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db), admin_user = Depends(get_current_actor_factory(["admin"]))):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    db.delete(task)
    db.commit()
    cache.invalidate("tasks")
    cache.invalidate("dashboard")
    return {"message": "Tarefa removida com sucesso"}
