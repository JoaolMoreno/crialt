from fastapi import APIRouter, Depends, UploadFile, File as FastAPIFile, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..api.dependencies import get_db, get_current_user, get_current_actor_factory, client_resource_permission
from ..models.user import User
from ..models.file import File
from ..models.project import Project
from ..schemas.file import FileRead, FileCreate, FileUpdate
from ..services.file_service import FileService

router = APIRouter()

@router.get("/", response_model=List[FileRead])
def get_files(db: Session = Depends(get_db), admin_user: User = Depends(get_current_actor_factory(["admin"]))):
    files = db.query(File).all()
    return files

@router.get("/project/{project_id}", response_model=List[FileRead])
def get_files_by_project(project_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor_factory())):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    client_ids = [str(client.id) for client in project.clients]
    client_resource_permission(client_ids, actor)
    files = db.query(File).filter(File.project_id == project_id).all()
    return files

@router.get("/client/{client_id}", response_model=List[FileRead])
def get_files_by_client(client_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor_factory())):
    # Verificar permissão para acessar arquivos do cliente
    client_resource_permission([client_id], actor)
    files = db.query(File).filter(File.client_id == client_id).all()
    return files

@router.get("/stage/{stage_id}", response_model=List[FileRead])
def get_files_by_stage(stage_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor_factory())):
    # Buscar a etapa e verificar permissão através do projeto
    from ..models.stage import Stage
    stage = db.get(Stage, stage_id)
    if not stage:
        raise HTTPException(status_code=404, detail="Etapa não encontrada")
    project = db.get(Project, stage.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado para a etapa")
    client_ids = [str(client.id) for client in project.clients]
    client_resource_permission(client_ids, actor)
    files = db.query(File).filter(File.stage_id == stage_id).all()
    return files

@router.get("/{file_id}", response_model=FileRead)
def get_file(file_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor_factory())):
    file = db.get(File, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    # Verificar permissão baseada no projeto ou cliente associado
    client_ids = []
    if file.project_id:
        project = db.get(Project, file.project_id)
        if project:
            client_ids = [str(client.id) for client in project.clients]
    elif file.client_id:
        client_ids = [str(file.client_id)]

    if client_ids:
        client_resource_permission(client_ids, actor)
    else:
        # Se não há cliente associado, só admin pode acessar
        if not (hasattr(actor, "role") and getattr(actor, "role", None) == "admin"):
            raise HTTPException(status_code=403, detail="Acesso negado")

    return file

@router.post("/", response_model=FileRead)
def upload_file(
    file: UploadFile = FastAPIFile(...),
    file_data: FileCreate = Depends(),
    db: Session = Depends(get_db),
    actor = Depends(get_current_actor_factory())
):
    # Verificar se o usuário tem permissão para fazer upload
    if file_data.project_id:
        project = db.get(Project, file_data.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
        client_ids = [str(client.id) for client in project.clients]
        client_resource_permission(client_ids, actor)
    elif file_data.client_id:
        client_resource_permission([str(file_data.client_id)], actor)

    # Se for usuário, definir uploaded_by_id como o próprio usuário
    if hasattr(actor, "role"):
        file_data.uploaded_by_id = actor.id

    file_bytes = file.file.read()
    service = FileService(db)
    saved_file = service.save_file(file_data, file_bytes)
    return FileRead.model_validate(saved_file)

@router.put("/{file_id}", response_model=FileRead)
def update_file(file_id: str, file_data: FileUpdate, db: Session = Depends(get_db), admin_user: User = Depends(get_current_actor_factory(["admin"]))):
    file = db.get(File, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    update_data = file_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(file, field, value)

    db.commit()
    db.refresh(file)
    return file

@router.delete("/{file_id}")
def delete_file(file_id: str, db: Session = Depends(get_db), admin_user: User = Depends(get_current_actor_factory(["admin"]))):
    file = db.get(File, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    service = FileService(db)
    success = service.delete_file(file_id)
    if not success:
        raise HTTPException(status_code=500, detail="Erro ao remover arquivo")

    return {"message": "Arquivo removido com sucesso"}
