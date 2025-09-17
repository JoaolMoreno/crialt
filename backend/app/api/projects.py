from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from ..api.dependencies import get_db, get_current_actor_factory, client_resource_permission
from ..models import User
from ..schemas.project import ProjectRead, ProjectCreate, ProjectUpdate, PaginatedProjects
from ..services.project_service import ProjectService

router = APIRouter()

@router.get("", response_model=PaginatedProjects)
async def get_projects(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_actor_factory(["admin"])),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_by: str = Query("created_at"),
    order_dir: str = Query("desc", pattern="^(asc|desc)$"),
    name: str = Query(None),
    status: str = Query(None),
    start_date: str = Query(None),
    client_id: str = Query(None),
    stage_name: str = Query(None),
    stage_type: str = Query(None),
    stage: str = Query(None),
    search: str = Query(None),
):
    service = ProjectService(db)
    return await run_in_threadpool(
        service.get_projects,
        limit, offset, order_by, order_dir, name, status, start_date, client_id, stage_name, stage_type, stage, search
    )

@router.get("/my", response_model=PaginatedProjects)
async def get_my_projects(
    db: Session = Depends(get_db),
    actor = Depends(get_current_actor_factory()),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_by: str = Query("created_at"),
    order_dir: str = Query("desc", pattern="^(asc|desc)$"),
    name: str = Query(None),
    status: str = Query(None),
    start_date: str = Query(None),
    client_id: str = Query(None),
    search: str = Query(None),
):
    service = ProjectService(db)
    return await run_in_threadpool(
        service.get_my_projects,
        actor, limit, offset, order_by, order_dir, name, status, start_date, client_id, search
    )

@router.get("/client/{client_id}", response_model=PaginatedProjects)
async def get_projects_by_client(
    client_id: str,
    db: Session = Depends(get_db),
    actor = Depends(get_current_actor_factory()),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_by: str = Query("created_at"),
    order_dir: str = Query("desc", pattern="^(asc|desc)$"),
    name: str = Query(None),
    status: str = Query(None),
    start_date: str = Query(None),
    search: str = Query(None),
):
    service = ProjectService(db)
    return await run_in_threadpool(
        service.get_projects_by_client,
        client_id, actor, limit, offset, order_by, order_dir, name, status, start_date, search, client_resource_permission
    )

@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(project_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor_factory())):
    service = ProjectService(db)
    return await run_in_threadpool(service.get_project, project_id, actor, client_resource_permission)

@router.post("", response_model=ProjectRead)
async def create_project(project_data: ProjectCreate, db: Session = Depends(get_db), admin_user: User = Depends(get_current_actor_factory(["admin"]))):
    service = ProjectService(db)
    return await run_in_threadpool(service.create_project, project_data, admin_user.id)

@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(project_id: str, project_data: ProjectUpdate, db: Session = Depends(get_db), admin_user: User = Depends(get_current_actor_factory(["admin"]))):
    service = ProjectService(db)
    return await run_in_threadpool(service.update_project, project_id, project_data)

@router.delete("/{project_id}")
async def delete_project(project_id: str, db: Session = Depends(get_db), admin_user: User = Depends(get_current_actor_factory(["admin"]))):
    service = ProjectService(db)
    return await run_in_threadpool(service.delete_project, project_id)

@router.get("/{project_id}/progress")
async def get_project_progress(project_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor_factory())):
    service = ProjectService(db)
    return await run_in_threadpool(service.get_project_progress, project_id, actor, client_resource_permission)

@router.put("/{project_id}/current-stage/{stage_id}")
async def update_current_stage(
    project_id: str,
    stage_id: str,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_actor_factory(["admin"]))
):
    service = ProjectService(db)
    return await run_in_threadpool(service.update_current_stage, project_id, stage_id)
