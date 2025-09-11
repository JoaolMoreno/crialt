from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..api.dependencies import get_db, get_current_user, get_current_actor_factory, client_resource_permission
from ..models import User, Client, Project
from ..schemas.project import ProjectRead, ProjectCreate, ProjectUpdate
from ..services.project_service import ProjectService

router = APIRouter()

def serialize_project(project):
    data = project.__dict__.copy()
    data["clients"] = [c.id for c in getattr(project, "clients", [])]
    data["stages"] = [s.id for s in getattr(project, "stages", [])]
    return data

@router.get("", response_model=List[ProjectRead])
def get_projects(db: Session = Depends(get_db), admin_user: User = Depends(get_current_actor_factory(["admin"]))):
    projects = db.query(Project).all()
    return [ProjectRead.model_validate(serialize_project(p)) for p in projects]

@router.get("/my", response_model=List[ProjectRead])
def get_my_projects(db: Session = Depends(get_db), actor = Depends(get_current_actor_factory())):
    # Admin: retorna todos os projetos
    if hasattr(actor, "role") and getattr(actor, "role", None) == "admin":
        projects = db.query(Project).all()
    # Cliente: retorna projetos vinculados ao cliente
    elif isinstance(actor, Client):
        projects = db.query(Project).join(Project.clients).filter(Client.id == actor.id).all()
    # Usuário comum: retorna projetos do seu client_id
    elif hasattr(actor, "client_id"):
        projects = db.query(Project).join(Project.clients).filter(Client.id == actor.client_id).all()
    else:
        projects = []
    return [ProjectRead.model_validate(serialize_project(p)) for p in projects]

@router.get("/client/{client_id}", response_model=List[ProjectRead])
def get_projects_by_client(client_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor_factory())):
    # Verificar permissão para acessar projetos do cliente
    client_resource_permission([client_id], actor)
    projects = db.query(Project).join(Project.clients).filter(Client.id == client_id).all()
    return [ProjectRead.model_validate(serialize_project(p)) for p in projects]

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
