from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from ..api.dependencies import get_db, get_current_actor_factory, client_resource_permission
from ..schemas.task import TaskRead, TaskCreate, TaskUpdate, PaginatedTasks
from ..services.task_service import TaskService

router = APIRouter()

@router.get("", response_model=PaginatedTasks)
async def get_tasks(
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
    service = TaskService(db)
    return await run_in_threadpool(
        service.get_tasks,
        limit, offset, order_by, order_dir, title, status, priority, due_date, stage_id, created_by_id, assigned_to_id
    )

@router.get("/stage/{stage_id}", response_model=List[TaskRead])
async def get_tasks_by_stage(stage_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor_factory())):
    service = TaskService(db)
    return await run_in_threadpool(service.get_tasks_by_stage, stage_id, actor, client_resource_permission)

@router.get("/project/{project_id}", response_model=List[TaskRead])
async def get_tasks_by_project(project_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor_factory())):
    service = TaskService(db)
    return await run_in_threadpool(service.get_tasks_by_project, project_id, actor, client_resource_permission)

@router.get("/{task_id}", response_model=TaskRead)
async def get_task(task_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor_factory())):
    service = TaskService(db)
    return await run_in_threadpool(service.get_task, task_id, actor, client_resource_permission)

@router.post("", response_model=TaskRead)
async def create_task(task_data: TaskCreate, db: Session = Depends(get_db), admin_user = Depends(get_current_actor_factory(["admin"]))):
    service = TaskService(db)
    return await run_in_threadpool(service.create_task, task_data)

@router.put("/{task_id}", response_model=TaskRead)
async def update_task(task_id: str, task_data: TaskUpdate, db: Session = Depends(get_db), admin_user = Depends(get_current_actor_factory(["admin"]))):
    service = TaskService(db)
    return await run_in_threadpool(service.update_task, task_id, task_data)

@router.delete("/{task_id}")
async def delete_task(task_id: str, db: Session = Depends(get_db), admin_user = Depends(get_current_actor_factory(["admin"]))):
    service = TaskService(db)
    return await run_in_threadpool(service.delete_task, task_id)
