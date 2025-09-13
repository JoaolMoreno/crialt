from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_, or_
from datetime import datetime, timedelta

from ..api.dependencies import get_db, get_current_actor_factory, client_resource_permission
from ..models import User, Client, Project, Stage
from ..schemas.client import ClientBasicRead
from ..schemas.file import FileRead
from ..schemas.project import ProjectRead, ProjectCreate, ProjectUpdate, PaginatedProjects
from ..schemas.stage import StageRead
from ..services.project_service import ProjectService
from ..utils.cache import cache

router = APIRouter()

def serialize_project(project):
    return {
        "id": project.id,
        "name": project.name,
        "description": getattr(project, "description", None),
        "total_value": project.total_value,
        "currency": project.currency,
        "start_date": project.start_date,
        "estimated_end_date": project.estimated_end_date,
        "actual_end_date": getattr(project, "actual_end_date", None),
        "status": project.status,
        "work_address": getattr(project, "work_address", None),
        "scope": getattr(project, "scope", None),
        "notes": getattr(project, "notes", None),
        "created_at": project.created_at,
        "updated_at": project.updated_at,
        "created_by_id": project.created_by_id,
        "clients": [ClientBasicRead.model_validate(c) for c in getattr(project, "clients", [])],
        "stages": [StageRead.model_validate(s) for s in getattr(project, "stages", [])],
        "files": [FileRead.model_validate(f) for f in getattr(project, "files", [])] if hasattr(project, "files") else [],
    }

def list_projects_query(query, limit, offset, order_by, order_dir, name=None, status=None, start_date=None, client_id=None):
    if name:
        query = query.filter(Project.name.ilike(f"%{name}%"))
    if status:
        query = query.filter(Project.status == status)
    if start_date:
        query = query.filter(Project.start_date == start_date)
    if client_id:
        query = query.join(Project.clients).filter(Client.id == client_id)
    # Ordenação
    if hasattr(Project, order_by):
        order_col = getattr(Project, order_by)
        if order_dir == "desc":
            order_col = order_col.desc()
        else:
            order_col = order_col.asc()
        query = query.order_by(order_col)
    return query

@router.get("", response_model=PaginatedProjects)
def get_projects(
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
):
    cache_params = {
        "limit": limit,
        "offset": offset,
        "order_by": order_by,
        "order_dir": order_dir,
        "name": name,
        "status": status,
        "start_date": start_date,
        "client_id": client_id
    }
    cached = cache.get("projects", cache_params)
    if cached:
        return cached
    query = list_projects_query(db.query(Project), limit, offset, order_by, order_dir, name, status, start_date, client_id)
    total = query.count()
    items = query.offset(offset).limit(limit).all()
    result = [ProjectRead.model_validate(serialize_project(p)) for p in items]
    paginated = PaginatedProjects(
        total=total,
        count=len(result),
        offset=offset,
        limit=limit,
        items=result
    )
    cache.set("projects", cache_params, paginated)
    return paginated

@router.get("/my", response_model=PaginatedProjects)
def get_my_projects(
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
):
    query = None
    # Admin: retorna todos os projetos
    if hasattr(actor, "role") and getattr(actor, "role", None) == "admin":
        query = db.query(Project)
    # Cliente: retorna projetos vinculados ao cliente
    elif isinstance(actor, Client):
        query = db.query(Project).join(Project.clients).filter(Client.id == actor.id)
    # Usuário comum: retorna projetos do seu client_id
    elif hasattr(actor, "client_id"):
        query = db.query(Project).join(Project.clients).filter(Client.id == actor.client_id)

    if query is not None:
        query = list_projects_query(query, limit, offset, order_by, order_dir, name, status, start_date, client_id)
        total = query.count()
        items = query.offset(offset).limit(limit).all()
        result = [ProjectRead.model_validate(serialize_project(p)) for p in items]
        return PaginatedProjects(
            total=total,
            count=len(result),
            offset=offset,
            limit=limit,
            items=result
        )
    else:
        return PaginatedProjects(
            total=0,
            count=0,
            offset=offset,
            limit=limit,
            items=[]
        )

@router.get("/client/{client_id}", response_model=PaginatedProjects)
def get_projects_by_client(
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
):
    client_resource_permission([client_id], actor)
    query = db.query(Project).join(Project.clients).filter(Client.id == client_id)
    query = list_projects_query(query, limit, offset, order_by, order_dir, name, status, start_date, client_id)
    total = query.count()
    items = query.offset(offset).limit(limit).all()
    result = [ProjectRead.model_validate(serialize_project(p)) for p in items]
    return PaginatedProjects(
        total=total,
        count=len(result),
        offset=offset,
        limit=limit,
        items=result
    )

@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor_factory())):
    service = ProjectService(db)
    project = service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    client_ids = [str(client.id) for client in project.clients]
    client_resource_permission(client_ids, actor)
    return ProjectRead.model_validate(serialize_project(project))

@router.post("", response_model=ProjectRead)
def create_project(project_data: ProjectCreate, db: Session = Depends(get_db), admin_user: User = Depends(get_current_actor_factory(["admin"]))):
    service = ProjectService(db)
    project = service.create_project(project_data, admin_user.id)
    cache.invalidate("projects")
    cache.invalidate("dashboard")
    return ProjectRead.model_validate(serialize_project(project))

@router.put("/{project_id}", response_model=ProjectRead)
def update_project(project_id: str, project_data: ProjectUpdate, db: Session = Depends(get_db), admin_user: User = Depends(get_current_actor_factory(["admin"]))):
    service = ProjectService(db)
    project = service.update_project(project_id, project_data)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    cache.invalidate("projects")
    cache.invalidate("dashboard")
    return ProjectRead.model_validate(serialize_project(project))

@router.delete("/{project_id}")
def delete_project(project_id: str, db: Session = Depends(get_db), admin_user: User = Depends(get_current_actor_factory(["admin"]))):
    service = ProjectService(db)
    success = service.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    cache.invalidate("projects")
    cache.invalidate("dashboard")
    return {"message": "Projeto removido com sucesso"}

@router.get("/{project_id}/progress")
def get_project_progress(project_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor_factory())):
    service = ProjectService(db)
    project = service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    client_ids = [str(client.id) for client in project.clients]
    client_resource_permission(client_ids, actor)
    progress = service.calculate_progress(project_id)
    return {"progress": progress}
