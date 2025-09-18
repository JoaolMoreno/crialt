from typing import List
from fastapi import APIRouter, Depends, UploadFile, File as FastAPIFile, Query, HTTPException, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool
import os

from ..api.dependencies import get_db, get_current_actor_factory, client_resource_permission
from ..models.user import User
from ..schemas.file import FileRead, FileCreate, FileUpdate, PaginatedFiles, FileCategory
from ..services.file_service import FileService

router = APIRouter()

@router.get("", response_model=PaginatedFiles)
async def get_files(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_actor_factory(["admin"])),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_by: str = Query("created_at"),
    order_dir: str = Query("desc", pattern="^(asc|desc)$"),
    original_name: str = Query(None),
    category: str = Query(None),
    project_id: str = Query(None),
    client_id: str = Query(None),
    stage_id: str = Query(None),
    uploaded_by_id: str = Query(None),
):
    service = FileService(db)
    return await run_in_threadpool(
        service.get_files,
        limit, offset, order_by, order_dir, original_name, category, project_id, client_id, stage_id, uploaded_by_id
    )

@router.get("/project/{project_id}", response_model=List[FileRead])
async def get_files_by_project(
    project_id: str,
    db: Session = Depends(get_db),
    actor = Depends(get_current_actor_factory())
):
    service = FileService(db)
    return await run_in_threadpool(service.get_files_by_project, project_id, client_resource_permission, actor)

@router.get("/client/{client_id}", response_model=List[FileRead])
async def get_files_by_client(
    client_id: str,
    db: Session = Depends(get_db),
    actor = Depends(get_current_actor_factory())
):
    service = FileService(db)
    return await run_in_threadpool(service.get_files_by_client, client_id, client_resource_permission, actor)

@router.get("/stage/{stage_id}", response_model=List[FileRead])
async def get_files_by_stage(
    stage_id: str,
    db: Session = Depends(get_db),
    actor = Depends(get_current_actor_factory())
):
    service = FileService(db)
    return await run_in_threadpool(service.get_files_by_stage, stage_id, client_resource_permission, actor)

@router.get("/{file_id}", response_model=FileRead)
async def get_file(
    file_id: str,
    db: Session = Depends(get_db),
    actor = Depends(get_current_actor_factory())
):
    service = FileService(db)
    return await run_in_threadpool(service.get_file, file_id, client_resource_permission, actor)

@router.post("", response_model=FileRead)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    category: str = Form(...),
    project_id: str = Form(None),
    client_id: str = Form(None),
    stage_id: str = Form(None),
    description: str = Form(None),
    db: Session = Depends(get_db),
    actor = Depends(get_current_actor_factory())
):
    from uuid import UUID

    # Criar FileCreate object
    file_data = FileCreate(
        original_name=file.filename or "unnamed",
        stored_name="",  # Será definido pelo service
        path="",  # Será definido pelo service
        size=0,  # Será definido pelo service
        mime_type=file.content_type or "application/octet-stream",
        category=FileCategory(category),
        description=description,
        project_id=UUID(project_id) if project_id else None,
        client_id=UUID(client_id) if client_id else None,
        stage_id=UUID(stage_id) if stage_id else None,
        uploaded_by_id=actor.id
    )

    service = FileService(db)
    return await run_in_threadpool(service.upload_file, file, file_data, actor, client_resource_permission)

@router.put("/{file_id}", response_model=FileRead)
async def update_file(file_id: str, file_data: FileUpdate, db: Session = Depends(get_db), admin_user: User = Depends(get_current_actor_factory(["admin"]))):
    service = FileService(db)
    return await run_in_threadpool(service.update_file, file_id, file_data)

@router.delete("/{file_id}")
async def delete_file(file_id: str, db: Session = Depends(get_db), admin_user: User = Depends(get_current_actor_factory(["admin"]))):
    service = FileService(db)
    return await run_in_threadpool(service.delete_file_api, file_id)

@router.get("/{file_id}/download")
async def download_file(file_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor_factory())):
    service = FileService(db)
    file_data = await run_in_threadpool(service.get_file, file_id, client_resource_permission, actor)
    file_path = file_data.path

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado no sistema de arquivos")

    return FileResponse(
        path=file_path,
        filename=file_data.original_name,
        media_type=file_data.mime_type
    )
