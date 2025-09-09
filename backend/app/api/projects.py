from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import get_db, get_current_user, get_current_actor, client_resource_permission, admin_required
from app.models import User, Client, Project
from app.schemas.project import ProjectRead, ProjectCreate, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter()

@router.get("/", response_model=List[ProjectRead])
def get_projects(db: Session = Depends(get_db), admin_user: User = Depends(admin_required)):
    projects = db.query(Project).all()
    return [ProjectRead.model_validate(p) for p in projects]

@router.get("/my", response_model=List[ProjectRead])
def get_my_projects(db: Session = Depends(get_db), actor = Depends(get_current_actor)):
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
    return [ProjectRead.model_validate(p) for p in projects]

@router.get("/client/{client_id}", response_model=List[ProjectRead])
def get_projects_by_client(client_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor)):
    # Verificar permissão para acessar projetos do cliente
    client_resource_permission([client_id], actor)
    projects = db.query(Project).join(Project.clients).filter(Client.id == client_id).all()
    return [ProjectRead.model_validate(p) for p in projects]

@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor)):
    service = ProjectService(db)
    project = service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    client_ids = [str(client.id) for client in project.clients]
    client_resource_permission(client_ids, actor)
    return ProjectRead.model_validate(project)

@router.post("/", response_model=ProjectRead)
def create_project(project_data: ProjectCreate, db: Session = Depends(get_db), admin_user: User = Depends(admin_required)):
    service = ProjectService(db)
    project = service.create_project(project_data, admin_user.id)
    return ProjectRead.model_validate(project)

@router.put("/{project_id}", response_model=ProjectRead)
def update_project(project_id: str, project_data: ProjectUpdate, db: Session = Depends(get_db), admin_user: User = Depends(admin_required)):
    service = ProjectService(db)
    project = service.update_project(project_id, project_data)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return ProjectRead.model_validate(project)

@router.delete("/{project_id}")
def delete_project(project_id: str, db: Session = Depends(get_db), admin_user: User = Depends(admin_required)):
    service = ProjectService(db)
    success = service.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return {"message": "Projeto removido com sucesso"}

@router.get("/{project_id}/progress")
def get_project_progress(project_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor)):
    service = ProjectService(db)
    project = service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    client_ids = [str(client.id) for client in project.clients]
    client_resource_permission(client_ids, actor)
    progress = service.calculate_progress(project_id)
    return {"progress": progress}
