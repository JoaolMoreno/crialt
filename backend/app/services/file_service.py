from sqlalchemy.orm import Session
from datetime import datetime
import os

from ..core.config import settings
from ..models.file import File
from ..schemas.file import FileCreate, FileCategory


class FileService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def save_file(self, file_data: FileCreate, file_bytes: bytes) -> File:
        # Validação de tipo e tamanho
        if file_data.category not in FileCategory:
            raise ValueError("Categoria de arquivo inválida.")
        if file_data.size > settings.MAX_FILE_SIZE:
            raise ValueError("Arquivo excede o tamanho máximo permitido.")
        ext = os.path.splitext(file_data.original_name)[1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise ValueError("Extensão de arquivo não permitida.")
        # Organização automática
        folder = os.path.join(settings.UPLOAD_DIR, file_data.category.value)
        os.makedirs(folder, exist_ok=True)
        stored_name = f"{datetime.utcnow().timestamp()}_{file_data.original_name}"
        path = os.path.join(folder, stored_name)
        with open(path, "wb") as f:
            f.write(file_bytes)
        # Versionamento: checar se já existe arquivo igual
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
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(file)
        self.db.commit()
        return file

    def delete_file(self, file_id: str) -> bool:
        file = self.db.get(File, file_id)
        if not file:
            return False
        # Remove arquivo físico
        try:
            if os.path.exists(file.path):
                os.remove(file.path)
        except Exception:
            pass
        self.db.delete(file)
        self.db.commit()
        return True
