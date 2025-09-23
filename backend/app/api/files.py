from typing import List
from fastapi import APIRouter, Depends, UploadFile, File as FastAPIFile, Query, HTTPException, Form, Body
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool
import os
from io import BytesIO
import zipfile

from ..api.dependencies import get_db, get_current_actor_factory, client_resource_permission
from ..models.user import User
from ..schemas.file import FileRead, FileCreate, FileUpdate, PaginatedFiles, FileCategory, FileReadPublic
from ..services.file_service import FileService
from ..models.project import Project
from ..core.config import settings

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

@router.get("/project/{project_id}", response_model=List[FileReadPublic])
async def get_files_by_project(
    project_id: str,
    db: Session = Depends(get_db),
    actor = Depends(get_current_actor_factory())
):
    service = FileService(db)
    return await run_in_threadpool(service.get_files_by_project, project_id, client_resource_permission, actor)

@router.get("/client/{client_id}", response_model=List[FileReadPublic])
async def get_files_by_client(
    client_id: str,
    db: Session = Depends(get_db),
    actor = Depends(get_current_actor_factory())
):
    service = FileService(db)
    return await run_in_threadpool(service.get_files_by_client, client_id, client_resource_permission, actor)

@router.get("/stage/{stage_id}", response_model=List[FileReadPublic])
async def get_files_by_stage(
    stage_id: str,
    db: Session = Depends(get_db),
    actor = Depends(get_current_actor_factory())
):
    service = FileService(db)
    return await run_in_threadpool(service.get_files_by_stage, stage_id, client_resource_permission, actor)

@router.get("/{file_id}", response_model=FileReadPublic|FileRead)
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
    category: str = Form(None),
    project_id: str = Form(None),
    client_id: str = Form(None),
    stage_id: str = Form(None),
    description: str = Form(None),
    db: Session = Depends(get_db),
    actor = Depends(get_current_actor_factory())
):
    from uuid import UUID

    detected_category = None
    if category:
        try:
            detected_category = FileCategory(category)
        except Exception:
            detected_category = FileCategory.document
    else:
        mime = file.content_type or "application/octet-stream"
        if mime.startswith("image/"):
            detected_category = FileCategory.image
        elif mime.startswith("video/"):
            detected_category = FileCategory.video
        else:
            detected_category = FileCategory.document

    file_data = FileCreate(
        original_name=file.filename or "unnamed",
        stored_name="",
        path="",
        size=0,
        mime_type=file.content_type or "application/octet-stream",
        category=detected_category,
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
    file_model = await run_in_threadpool(service.get_file_internal, file_id, actor, client_resource_permission)
    file_path = file_model.path
    # valida path dentro do diretório de upload
    root = os.path.realpath(settings.UPLOAD_DIR)
    real = os.path.realpath(file_path)
    if not real.startswith(root + os.sep) and real != root:
        raise HTTPException(status_code=400, detail="Caminho de arquivo inválido")
    if not os.path.exists(real):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado no sistema de arquivos")

    safe_name = FileService.sanitize_filename(file_model.original_name)
    return FileResponse(
        path=real,
        filename=safe_name,
        media_type=file_model.mime_type
    )

@router.get("/project/{project_id}/download")
async def download_project_files(
    project_id: str,
    db: Session = Depends(get_db),
    actor = Depends(get_current_actor_factory())
):
    service = FileService(db)
    files = await run_in_threadpool(service.get_files_by_project, project_id, client_resource_permission, actor)
    if not files:
        raise HTTPException(status_code=404, detail="Nenhum arquivo encontrado para este projeto.")
    project = db.query(Project).filter(Project.id == project_id).first()
    project_name = project.name if project else f"projeto_{project_id}"
    safe_project_name = FileService.sanitize_filename(project_name)
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            # precisamos obter o modelo interno para pegar o path real
            file_model = await run_in_threadpool(service.get_file_internal, str(file.id), actor, client_resource_permission)
            if not file_model.path:
                continue
            real = os.path.realpath(file_model.path)
            root = os.path.realpath(settings.UPLOAD_DIR)
            if not real.startswith(root + os.sep) and real != root:
                continue
            if not os.path.exists(real):
                continue
            arcname = FileService.sanitize_filename(file_model.original_name)
            zipf.write(real, arcname=arcname)
    zip_buffer.seek(0)
    zip_filename = f"{safe_project_name}.zip"
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{zip_filename}"'}
    )

@router.post("/download")
async def download_selected_files(
    file_ids: list = Body(..., embed=True),
    db: Session = Depends(get_db),
    actor = Depends(get_current_actor_factory())
):
    service = FileService(db)
    files = []
    for file_id in file_ids:
        try:
            file_model = await run_in_threadpool(service.get_file_internal, str(file_id), actor, client_resource_permission)
            files.append(file_model)
        except Exception:
            continue
    if not files:
        raise HTTPException(status_code=404, detail="Nenhum arquivo encontrado.")
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        root = os.path.realpath(settings.UPLOAD_DIR)
        for file_model in files:
            if not file_model.path:
                continue
            real = os.path.realpath(file_model.path)
            if not real.startswith(root + os.sep) and real != root:
                continue
            if not os.path.exists(real):
                continue
            arcname = FileService.sanitize_filename(file_model.original_name)
            zipf.write(real, arcname=arcname)
    zip_buffer.seek(0)
    zip_filename = "arquivos.zip"
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{zip_filename}"'}
    )
