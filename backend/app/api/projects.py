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
    query = list_projects_query(db.query(Project), limit, offset, order_by, order_dir, name, status, start_date, client_id)
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
    return ProjectRead.model_validate(serialize_project(project))

@router.put("/{project_id}", response_model=ProjectRead)
def update_project(project_id: str, project_data: ProjectUpdate, db: Session = Depends(get_db), admin_user: User = Depends(get_current_actor_factory(["admin"]))):
    service = ProjectService(db)
    project = service.update_project(project_id, project_data)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return ProjectRead.model_validate(serialize_project(project))

@router.delete("/{project_id}")
def delete_project(project_id: str, db: Session = Depends(get_db), admin_user: User = Depends(get_current_actor_factory(["admin"]))):
    service = ProjectService(db)
    success = service.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
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

@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    first_day_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_6_months = [(now.replace(day=1) - timedelta(days=30*i)) for i in range(6)]
    months = [(d.month, d.year) for d in reversed(last_6_months)]

    # Total de clientes ativos
    total_clients = db.query(func.count()).select_from(Client).filter(Client.is_active == True).scalar()

    # Projetos ativos
    active_projects = db.query(func.count()).select_from(Project).filter(Project.status == "active").scalar()

    # Projetos finalizados no mês atual
    completed_projects_this_month = db.query(func.count()).select_from(Project).filter(
        Project.status == "completed",
        Project.actual_end_date >= first_day_month,
        Project.actual_end_date < now.replace(day=now.day+1)
    ).scalar()

    # Receita do mês atual
    month_revenue = db.query(func.coalesce(func.sum(Project.total_value), 0)).filter(
        Project.status == "completed",
        Project.actual_end_date >= first_day_month,
        Project.actual_end_date < now.replace(day=now.day+1)
    ).scalar()

    # 5 projetos mais recentes
    recent_projects = db.query(Project).order_by(Project.created_at.desc()).limit(5).all()
    recent_projects_serialized = [serialize_project(p) for p in recent_projects]

    # Contagem de projetos por status
    status_list = ["active", "paused", "completed", "cancelled", "draft"]
    projects_status_counts = {}
    for status in status_list:
        count = db.query(func.count()).select_from(Project).filter(Project.status == status).scalar()
        projects_status_counts[status] = count

    # Receita dos últimos 6 meses
    revenue_by_month = []
    for month, year in months:
        start = datetime(year, month, 1)
        if month == 12:
            end = datetime(year+1, 1, 1)
        else:
            end = datetime(year, month+1, 1)
        value = db.query(func.coalesce(func.sum(Project.total_value), 0)).filter(
            Project.status == "completed",
            Project.actual_end_date >= start,
            Project.actual_end_date < end
        ).scalar()
        revenue_by_month.append({
            "month": start.strftime("%b"),
            "year": str(start.year)[-2:],
            "value": float(value) if value else 0
        })

    # Etapas próximas do prazo (próximos 7 dias, não completadas)
    near_deadline = now + timedelta(days=7)
    stages_near_deadline = db.query(func.count()).select_from(Stage).filter(
        Stage.status != "completed",
        Stage.planned_end_date >= now.date(),
        Stage.planned_end_date <= near_deadline.date()
    ).scalar()

    return {
        "total_clients": total_clients,
        "active_projects": active_projects,
        "completed_projects_this_month": completed_projects_this_month,
        "month_revenue": float(month_revenue) if month_revenue else 0,
        "recent_projects": recent_projects_serialized,
        "projects_status_counts": projects_status_counts,
        "revenue_by_month": revenue_by_month,
        "stages_near_deadline": stages_near_deadline
    }
