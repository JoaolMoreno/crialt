from sqlalchemy.orm import Session
from datetime import datetime, timezone
import os
from ..core.config import settings
from ..models.file import File
from ..schemas.file import FileCreate, FileCategory, FileUpdate
from fastapi import HTTPException, UploadFile
from ..models.project import Project
from ..schemas.file import FileRead, PaginatedFiles
from ..utils.cache import cache
from typing import List, Optional, Dict
import logging


class FileService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.logger = logging.getLogger(__name__)

    def save_file(self, file_data: FileCreate, file_bytes: bytes) -> File:
        if file_data.category not in FileCategory:
            raise ValueError("Categoria de arquivo inválida.")
        if file_data.size > settings.MAX_FILE_SIZE:
            raise ValueError("Arquivo excede o tamanho máximo permitido.")
        ext = os.path.splitext(file_data.original_name)[1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise ValueError("Extensão de arquivo não permitida.")
        folder = os.path.join(settings.UPLOAD_DIR, file_data.category.value)
        os.makedirs(folder, exist_ok=True)
        stored_name = f"{datetime.now(timezone.utc).timestamp()}_{file_data.original_name}"
        path = os.path.join(folder, stored_name)
        with open(path, "wb") as f:
            f.write(file_bytes)
        file = File(
            original_name=file_data.original_name,
            stored_name=stored_name,
            path=path,
            size=file_data.size,
            mime_type=file_data.mime_type,
            category=file_data.category,
            description=file_data.description,
            project_id=file_data.project_id,
            client_id=file_data.client_id,
            stage_id=file_data.stage_id,
            uploaded_by_id=file_data.uploaded_by_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        self.db.add(file)
        self.db.commit()
        return file

    def delete_file(self, file_id: str) -> bool:
        file = self.db.get(File, file_id)
        if not file:
            return False
        try:
            file_path = str(file.path) if not isinstance(file.path, str) else file.path
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass
        self.db.delete(file)
        self.db.commit()
        return True

    def get_files(self, limit: int, offset: int, order_by: str, order_dir: str, original_name: Optional[str], category: Optional[str], project_id: Optional[str], client_id: Optional[str], stage_id: Optional[str], uploaded_by_id: Optional[str]) -> PaginatedFiles:
        cache_params = {
            "limit": limit,
            "offset": offset,
            "order_by": order_by,
            "order_dir": order_dir,
            "original_name": original_name,
            "category": category,
            "project_id": project_id,
            "client_id": client_id,
            "stage_id": stage_id,
            "uploaded_by_id": uploaded_by_id
        }
        cached = cache.get("files", cache_params)
        if cached:
            self.logger.info(f"[CACHE] get_files: params={cache_params}")
            return cached
        self.logger.info(f"[DB] get_files: params={cache_params}")
        query = self.db.query(File)
        if original_name:
            query = query.filter(File.original_name.ilike(f"%{original_name}%"))
        if category:
            query = query.filter(File.category == category)
        if project_id:
            query = query.filter(File.project_id == project_id)
        if client_id:
            query = query.filter(File.client_id == client_id)
        if stage_id:
            query = query.filter(File.stage_id == stage_id)
        if uploaded_by_id:
            query = query.filter(File.uploaded_by_id == uploaded_by_id)
        if hasattr(File, order_by):
            order_col = getattr(File, order_by)
            if order_dir == "desc":
                order_col = order_col.desc()
            else:
                order_col = order_col.asc()
            query = query.order_by(order_col)
        total = query.count()
        items = query.offset(offset).limit(limit).all()
        result = PaginatedFiles(
            total=total,
            count=len(items),
            offset=offset,
            limit=limit,
            items=[FileRead.model_validate(f, from_attributes=True) for f in items]
        )
        cache.set("files", cache_params, result)
        return result

    def get_files_by_project(self, project_id: str, client_resource_permission, actor) -> List[FileRead]:
        project = self.db.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
        client_ids = [str(client.id) for client in project.clients]
        client_resource_permission(client_ids, actor)
        files = self.db.query(File).filter(File.project_id == project_id).all()
        return [FileRead.model_validate(f, from_attributes=True) for f in files]

    def get_files_by_client(self, client_id: str, client_resource_permission, actor) -> List[FileRead]:
        client_resource_permission([client_id], actor)
        files = self.db.query(File).filter(File.client_id == client_id).all()
        return [FileRead.model_validate(f, from_attributes=True) for f in files]

    def get_files_by_stage(self, stage_id: str, client_resource_permission, actor) -> List[FileRead]:
        from ..models.stage import Stage
        stage = self.db.get(Stage, stage_id)
        if not stage:
            raise HTTPException(status_code=404, detail="Etapa não encontrada")
        project = self.db.get(Project, stage.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Projeto não encontrado para a etapa")
        client_ids = [str(client.id) for client in project.clients]
        client_resource_permission(client_ids, actor)
        files = self.db.query(File).filter(File.stage_id == stage_id).all()
        return [FileRead.model_validate(f, from_attributes=True) for f in files]

    def get_file(self, file_id: str, client_resource_permission, actor) -> FileRead:
        file = self.db.get(File, file_id)
        if not file:
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        client_ids = []
        if file.project_id:
            project = self.db.get(Project, file.project_id)
            if project:
                client_ids = [str(client.id) for client in project.clients]
        elif file.client_id:
            client_ids = [str(file.client_id)]
        if client_ids:
            client_resource_permission(client_ids, actor)
        else:
            if not (hasattr(actor, "role") and getattr(actor, "role", None) == "admin"):
                raise HTTPException(status_code=403, detail="Acesso negado")
        return FileRead.model_validate(file, from_attributes=True)

    def upload_file(self, file: UploadFile, file_data: FileCreate, actor, client_resource_permission) -> FileRead:
        if file_data.project_id:
            project = self.db.get(Project, file_data.project_id)
            if not project:
                raise HTTPException(status_code=404, detail="Projeto não encontrado")
            client_ids = [str(client.id) for client in project.clients]
            client_resource_permission(client_ids, actor)
        elif file_data.client_id:
            client_resource_permission([str(file_data.client_id)], actor)

        if hasattr(actor, "id"):
            file_data.uploaded_by_id = actor.id

        # Criar FileCreate com dados do arquivo real
        file_bytes = file.file.read()

        # Atualizar file_data com informações do arquivo real
        file_data.original_name = file.filename or "unnamed"
        file_data.size = len(file_bytes)
        file_data.mime_type = file.content_type or "application/octet-stream"

        saved_file = self.save_file(file_data, file_bytes)
        cache.invalidate("files")
        cache.invalidate("dashboard")
        return FileRead.model_validate(saved_file, from_attributes=True)

    def update_file(self, file_id: str, file_data: FileUpdate) -> FileRead:
        file = self.db.get(File, file_id)
        if not file:
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        update_data = file_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(file, field, value)
        self.db.commit()
        self.db.refresh(file)
        cache.invalidate("files")
        cache.invalidate("dashboard")
        return FileRead.model_validate(file, from_attributes=True)

    def delete_file_api(self, file_id: str) -> Dict[str, str]:
        file = self.db.get(File, file_id)
        if not file:
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        success = self.delete_file(file_id)
        if not success:
            raise HTTPException(status_code=500, detail="Erro ao remover arquivo")
        cache.invalidate("files")
        cache.invalidate("dashboard")
        return {"message": "Arquivo removido com sucesso"}
