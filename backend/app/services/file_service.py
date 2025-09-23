from sqlalchemy.orm import Session
from datetime import datetime, timezone
import os
import re
from uuid import uuid4
from ..core.config import settings
from ..models.file import File
from ..schemas.file import FileCreate, FileCategory, FileUpdate, FileRead, PaginatedFiles, FileReadPublic
from fastapi import HTTPException, UploadFile
from ..models.project import Project
from ..utils.cache import cache
from typing import List, Optional, Dict, Any
import logging


class FileService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def sanitize_filename(name: str, max_length: int = 128) -> str:
        base = os.path.basename(name or "")
        # remove caracteres de controle e separadores
        base = base.replace("\\", "_").replace("/", "_")
        # somente caracteres seguros
        base = re.sub(r"[^A-Za-z0-9._ -]", "_", base)
        # colapsa espaços
        base = re.sub(r"\s+", " ", base).strip()
        if len(base) > max_length:
            root, ext = os.path.splitext(base)
            keep = max_length - len(ext)
            base = (root[:keep] if keep > 0 else root[:max_length]) + ext
        # evita nomes vazios
        return base or "arquivo"

    @staticmethod
    def _ensure_within_upload_dir(path: str) -> str:
        root = os.path.realpath(settings.UPLOAD_DIR)
        real = os.path.realpath(path)
        if not real.startswith(root + os.sep) and real != root:
            raise HTTPException(status_code=400, detail="Caminho de arquivo inválido")
        if os.path.islink(real):
            raise HTTPException(status_code=400, detail="Links simbólicos não são permitidos")
        return real

    def _build_storage_path(self, original_name: str, category: FileCategory) -> tuple[str, str]:
        ext = os.path.splitext(original_name)[1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Tipo de arquivo não permitido.")
        folder = os.path.join(settings.UPLOAD_DIR, category.value)
        os.makedirs(folder, exist_ok=True)
        stored_name = f"{uuid4().hex}{ext}"
        path = os.path.join(folder, stored_name)
        real = self._ensure_within_upload_dir(path)
        return stored_name, real

    def save_file(self, file_data: FileCreate, file_bytes: bytes) -> File:
        # Mantém compatibilidade, mas passa pelo mesmo funil de validação
        if file_data.category not in FileCategory:
            raise HTTPException(status_code=400, detail="Categoria de arquivo não é válida.")
        if file_data.size > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="O arquivo é muito grande.")
        safe_original = self.sanitize_filename(file_data.original_name)
        stored_name, path = self._build_storage_path(safe_original, file_data.category)
        with open(path, "wb") as f:
            f.write(file_bytes)
        file = File(
            original_name=safe_original,
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

    def upload_file(self, file: UploadFile, file_data: FileCreate, actor, client_resource_permission) -> FileRead:
        # Autorização por recurso
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

        safe_original = self.sanitize_filename(file.filename or "unnamed")
        file_data.original_name = safe_original
        file_data.mime_type = file.content_type or "application/octet-stream"

        # Preparar path de destino e stored_name
        stored_name, dest_path = self._build_storage_path(safe_original, file_data.category)

        # Upload em streaming com limite de tamanho
        total = 0
        try:
            with open(dest_path, "wb") as out:
                while True:
                    chunk = file.file.read(1024 * 1024)  # 1MB
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > settings.MAX_FILE_SIZE:
                        raise HTTPException(status_code=400, detail="O arquivo é muito grande.")
                    out.write(chunk)
        except Exception:
            # limpa arquivo parcial
            try:
                if os.path.exists(dest_path):
                    os.remove(dest_path)
            except Exception:
                pass
            raise

        file_data.size = total
        file_data.stored_name = stored_name
        file_data.path = dest_path

        file_model = File(
            original_name=file_data.original_name,
            stored_name=file_data.stored_name,
            path=file_data.path,
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
        self.db.add(file_model)
        self.db.commit()
        cache.invalidate("files")
        cache.invalidate("dashboard")
        return FileRead.model_validate(file_model, from_attributes=True)

    def delete_file(self, file_id: str) -> bool:
        file = self.db.get(File, file_id)
        if not file:
            return False
        try:
            file_path = str(file.path) if not isinstance(file.path, str) else file.path
            real = self._ensure_within_upload_dir(file_path)
            if os.path.exists(real):
                os.remove(real)
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
        from ..models.file import File as FileModel
        query = self.db.query(FileModel)
        if original_name:
            query = query.filter(FileModel.original_name.ilike(f"%{original_name}%"))
        if category:
            query = query.filter(FileModel.category == category)
        if project_id:
            query = query.filter(FileModel.project_id == project_id)
        if client_id:
            query = query.filter(FileModel.client_id == client_id)
        if stage_id:
            query = query.filter(FileModel.stage_id == stage_id)
        if uploaded_by_id:
            query = query.filter(FileModel.uploaded_by_id == uploaded_by_id)
        if hasattr(FileModel, order_by):
            order_col = getattr(FileModel, order_by)
            order_col = order_col.desc() if order_dir == "desc" else order_col.asc()
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

    def get_files_by_project(self, project_id: str, client_resource_permission, actor) -> List[FileReadPublic]:
        project = self.db.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
        client_ids = [str(client.id) for client in project.clients]
        client_resource_permission(client_ids, actor)
        from ..models.file import File as FileModel
        files = self.db.query(FileModel).filter(FileModel.project_id == project_id).all()
        return [FileReadPublic.model_validate(f, from_attributes=True) for f in files]

    def get_files_by_client(self, client_id: str, client_resource_permission, actor) -> List[FileReadPublic]:
        client_resource_permission([client_id], actor)
        from ..models.file import File as FileModel
        files = self.db.query(FileModel).filter(FileModel.client_id == client_id).all()
        return [FileReadPublic.model_validate(f, from_attributes=True) for f in files]

    def get_files_by_stage(self, stage_id: str, client_resource_permission, actor) -> List[FileReadPublic]:
        from ..models.stage import Stage
        stage = self.db.get(Stage, stage_id)
        if not stage:
            raise HTTPException(status_code=404, detail="Etapa não encontrada")
        project = self.db.get(Project, stage.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Projeto não encontrado para a etapa")
        client_ids = [str(client.id) for client in project.clients]
        client_resource_permission(client_ids, actor)
        from ..models.file import File as FileModel
        files = self.db.query(FileModel).filter(FileModel.stage_id == stage_id).all()
        return [FileReadPublic.model_validate(f, from_attributes=True) for f in files]

    def get_file(self, file_id: str, client_resource_permission, actor) -> FileReadPublic|FileRead:
        from ..models.file import File as FileModel
        file = self.db.get(FileModel, file_id)
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

        if hasattr(actor, "role") and getattr(actor, "role", None) == "admin":
            return FileRead.model_validate(file, from_attributes=True)
        return FileReadPublic.model_validate(file, from_attributes=True)

    def get_file_internal(self, file_id: str, actor, client_resource_permission) -> File:
        from ..models.file import File as FileModel
        file = self.db.get(FileModel, file_id)
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
        return file

    def update_file(self, file_id: str, file_data: FileUpdate) -> FileRead:
        from ..models.file import File as FileModel
        file = self.db.get(FileModel, file_id)
        if not file:
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        update_data = file_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(file, field, value)
        file.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(file)
        cache.invalidate("files")
        cache.invalidate("dashboard")
        return FileRead.model_validate(file, from_attributes=True)

    def delete_file_api(self, file_id: str) -> Dict[str, str]:
        from ..models.file import File as FileModel
        file = self.db.get(FileModel, file_id)
        if not file:
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        success = self.delete_file(file_id)
        if not success:
            raise HTTPException(status_code=500, detail="Erro ao remover arquivo")
        cache.invalidate("files")
        cache.invalidate("dashboard")
        return {"message": "Arquivo removido com sucesso"}
