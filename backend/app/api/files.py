from typing import List
from fastapi import APIRouter, Depends, UploadFile, File as FastAPIFile, Query
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from ..api.dependencies import get_db, get_current_actor_factory, client_resource_permission
from ..models.user import User
from ..schemas.file import FileRead, FileCreate, FileUpdate, PaginatedFiles
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
async def get_files_by_project(project_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor_factory())):
    service = FileService(db)
    return await run_in_threadpool(service.get_files_by_project, project_id, client_resource_permission, actor)

@router.get("/client/{client_id}", response_model=List[FileRead])
async def get_files_by_client(client_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor_factory())):
    service = FileService(db)
    return await run_in_threadpool(service.get_files_by_client, client_id, client_resource_permission, actor)

@router.get("/stage/{stage_id}", response_model=List[FileRead])
async def get_files_by_stage(stage_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor_factory())):
    service = FileService(db)
    return await run_in_threadpool(service.get_files_by_stage, stage_id, client_resource_permission, actor)

@router.get("/{file_id}", response_model=FileRead)
async def get_file(file_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor_factory())):
    service = FileService(db)
    return await run_in_threadpool(service.get_file, file_id, client_resource_permission, actor)

@router.post("", response_model=FileRead)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    file_data: FileCreate = Depends(),
    db: Session = Depends(get_db),
    actor = Depends(get_current_actor_factory())
):
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
