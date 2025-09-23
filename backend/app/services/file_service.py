from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone, timedelta
import os
import re
import time
import hashlib
from uuid import uuid4
from ..core.config import settings
from ..models.file import File
from ..models.chunked_upload import ChunkedUpload
from ..schemas.file import FileCreate, FileCategory, FileUpdate, FileRead, PaginatedFiles, FileReadPublic
from ..schemas.chunked_upload import (
    ChunkedUploadInitiate, ChunkedUploadResponse, ChunkUploadResponse,
    ChunkedUploadStatus, ChunkedUploadComplete
)
from fastapi import HTTPException, UploadFile
from ..models.project import Project
from ..utils.cache import cache
from typing import List, Optional, Dict, Any
import logging


class FileService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.temp_dir = os.path.join(settings.UPLOAD_DIR, "temp_chunks")
        os.makedirs(self.temp_dir, exist_ok=True)
        self.max_retries = 3
        self.retry_delay = 0.5
        self.chunk_timeout = settings.CHUNK_UPLOAD_TIMEOUT

    @staticmethod
    def sanitize_filename(name: str, max_length: int = 128) -> str:
        base = os.path.basename(name or "")
        base = base.replace("\\", "_").replace("/", "_")
        base = re.sub(r"[^A-Za-z0-9._-]", "_", base)
        base = re.sub(r"\s+", "", base)
        if len(base) > max_length:
            root, ext = os.path.splitext(base)
            keep = max_length - len(ext)
            base = (root[:keep] if keep > 0 else root[:max_length]) + ext
        return base or "arquivo"

    def _validate_file_type(self, filename: str, mime_type: str) -> None:
        """Valida o tipo de arquivo baseado na extensão e MIME type"""
        if not filename:
            raise HTTPException(status_code=400, detail="Nome do arquivo é obrigatório")

        ext = os.path.splitext(filename)[1].lower()
        if not ext:
            raise HTTPException(status_code=400, detail="Arquivo deve ter uma extensão")

        if ext not in settings.ALLOWED_EXTENSIONS:
            allowed_list = ", ".join(settings.ALLOWED_EXTENSIONS)
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de arquivo não permitido. Extensões permitidas: {allowed_list}"
            )

        if mime_type:
            dangerous_mimes = [
                "application/x-executable", "application/x-msdownload",
                "application/x-msdos-program", "application/x-dosexec",
                "text/x-shellscript", "application/x-sh"
            ]

            if mime_type in dangerous_mimes:
                raise HTTPException(status_code=400, detail="Tipo de arquivo não permitido")

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
        filename = file.filename or "unnamed"
        mime_type = file.content_type or "application/octet-stream"
        self._validate_file_type(filename, mime_type)

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

        safe_original = self.sanitize_filename(filename)
        file_data.original_name = safe_original
        file_data.mime_type = mime_type

        stored_name, dest_path = self._build_storage_path(safe_original, file_data.category)

        total = 0
        try:
            with open(dest_path, "wb") as out:
                while True:
                    chunk = file.file.read(1024 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > settings.MAX_FILE_SIZE:
                        raise HTTPException(status_code=400, detail="O arquivo é muito grande.")
                    out.write(chunk)
        except Exception:
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

    def initiate_upload(self, upload_data: ChunkedUploadInitiate, actor) -> ChunkedUploadResponse:
        self.logger.info(f"Iniciando upload chunked: {upload_data.filename}, {upload_data.total_chunks} chunks")

        self._validate_file_type(upload_data.filename, upload_data.mime_type)

        if upload_data.total_size > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"Arquivo muito grande. Máximo: {settings.MAX_FILE_SIZE} bytes")

        if upload_data.chunk_size > settings.MAX_CHUNK_SIZE:
            raise HTTPException(status_code=400, detail=f"Chunk muito grande. Máximo: {settings.MAX_CHUNK_SIZE} bytes")

        if upload_data.total_chunks <= 0 or upload_data.total_chunks > 10000:
            raise HTTPException(status_code=400, detail="Número de chunks inválido (1-10000)")

        if upload_data.project_id:
            project = self.db.get(Project, upload_data.project_id)
            if not project:
                raise HTTPException(status_code=404, detail="Projeto não encontrado")
            from ..api.dependencies import client_resource_permission
            client_ids = [str(client.id) for client in project.clients]
            client_resource_permission(client_ids, actor)
        elif upload_data.client_id:
            from ..api.dependencies import client_resource_permission
            client_resource_permission([str(upload_data.client_id)], actor)

        upload_id = f"{uuid4().hex}_{int(datetime.now(timezone.utc).timestamp())}"
        expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.CHUNKED_UPLOAD_EXPIRY_HOURS)

        chunk_dir = os.path.join(self.temp_dir, upload_id)
        try:
            os.makedirs(chunk_dir, exist_ok=True)
        except OSError as e:
            self.logger.error(f"Erro ao criar diretório de chunks: {e}")
            raise HTTPException(status_code=500, detail="Erro interno do servidor")

        try:
            chunked_upload = ChunkedUpload(
                upload_id=upload_id,
                filename=upload_data.filename,
                total_chunks=upload_data.total_chunks,
                chunk_size=upload_data.chunk_size,
                total_size=upload_data.total_size,
                file_checksum=upload_data.file_checksum,
                mime_type=upload_data.mime_type,
                category=upload_data.category,
                project_id=upload_data.project_id,
                client_id=upload_data.client_id,
                stage_id=upload_data.stage_id,
                description=upload_data.description,
                uploaded_by_id=actor.id,
                expires_at=expires_at,
                uploaded_chunks=""
            )

            self.db.add(chunked_upload)
            self.db.commit()

            self.logger.info(f"Upload iniciado com sucesso: {upload_id}")

            return ChunkedUploadResponse(
                upload_id=upload_id,
                expires_at=expires_at,
                uploaded_chunks=[]
            )

        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Erro ao criar upload no banco: {e}")
            try:
                if os.path.exists(chunk_dir):
                    os.rmdir(chunk_dir)
            except:
                pass
            raise HTTPException(status_code=500, detail="Erro ao iniciar upload")

    def upload_chunk(self, upload_id: str, chunk_number: int, chunk_file: UploadFile) -> ChunkUploadResponse:
        start_time = time.time()
        self.logger.debug(f"Iniciando upload chunk {chunk_number} para upload {upload_id}")

        for attempt in range(self.max_retries):
            try:
                if time.time() - start_time > self.chunk_timeout:
                    raise HTTPException(status_code=408, detail="Timeout no upload do chunk")

                result = self._upload_chunk_attempt(upload_id, chunk_number, chunk_file, attempt)
                self.logger.debug(f"Chunk {chunk_number} enviado com sucesso (tentativa {attempt + 1})")
                return result

            except HTTPException as e:
                self.logger.error(f"Erro HTTP no chunk {chunk_number}: {e.detail}")
                raise
            except Exception as e:
                self.logger.warning(f"Tentativa {attempt + 1} falhou para chunk {chunk_number}: {e}")
                if attempt == self.max_retries - 1:
                    self.logger.error(f"Todas as tentativas falharam para chunk {chunk_number}: {e}")
                    raise HTTPException(status_code=500, detail=f"Erro ao salvar chunk após {self.max_retries} tentativas")

                delay = self.retry_delay * (2 ** attempt) + (time.time() % 1) * 0.1
                time.sleep(delay)

    def _upload_chunk_attempt(self, upload_id: str, chunk_number: int, chunk_file: UploadFile, attempt: int) -> ChunkUploadResponse:
        chunk_file.file.seek(0)

        try:
            upload = self.db.query(ChunkedUpload).filter(
                ChunkedUpload.upload_id == upload_id
            ).first()

            if not upload:
                raise HTTPException(status_code=404, detail="Upload não encontrado")

            if upload.is_completed:
                raise HTTPException(status_code=400, detail="Upload já foi completado")

            if datetime.now(timezone.utc) > upload.expires_at:
                self.logger.warning(f"Upload expirado: {upload_id}")
                raise HTTPException(status_code=400, detail="Upload expirado")

            if chunk_number < 1 or chunk_number > upload.total_chunks:
                raise HTTPException(status_code=400, detail=f"Número do chunk inválido: {chunk_number}")

            uploaded_chunks = self._parse_uploaded_chunks(upload.uploaded_chunks)
            if chunk_number in uploaded_chunks:
                self.logger.debug(f"Chunk {chunk_number} já foi enviado anteriormente")
                return ChunkUploadResponse(
                    chunk_number=chunk_number,
                    received=True,
                    upload_progress=len(uploaded_chunks) / upload.total_chunks * 100,
                    uploaded_chunks=uploaded_chunks
                )

            chunk_dir = os.path.join(self.temp_dir, upload_id)
            chunk_path = os.path.join(chunk_dir, f"chunk_{chunk_number:06d}")
            chunk_lock_path = f"{chunk_path}.lock"
            temp_chunk_path = f"{chunk_path}.tmp.{attempt}"

            if os.path.exists(chunk_lock_path):
                lock_age = time.time() - os.path.getmtime(chunk_lock_path)
                if lock_age < 30:
                    raise Exception(f"Chunk {chunk_number} está sendo processado por outra operação")
                else:
                    try:
                        os.remove(chunk_lock_path)
                    except:
                        pass

            try:
                with open(chunk_lock_path, 'w') as lock_file:
                    lock_file.write(str(os.getpid()))
            except:
                raise Exception(f"Não foi possível criar lock para chunk {chunk_number}")

            try:
                chunk_size = 0
                chunk_hash = hashlib.md5()

                try:
                    with open(temp_chunk_path, "wb") as f:
                        while True:
                            data = chunk_file.file.read(8192)
                            if not data:
                                break
                            chunk_size += len(data)
                            chunk_hash.update(data)
                            f.write(data)

                    if chunk_size == 0:
                        raise Exception("Chunk vazio recebido")

                    if chunk_size > settings.MAX_CHUNK_SIZE:
                        raise Exception(f"Chunk muito grande: {chunk_size} bytes")

                    if os.path.exists(chunk_path):
                        with open(chunk_path, "rb") as existing_file:
                            existing_hash = hashlib.md5()
                            while True:
                                data = existing_file.read(8192)
                                if not data:
                                    break
                                existing_hash.update(data)

                        if existing_hash.hexdigest() == chunk_hash.hexdigest():
                            os.remove(temp_chunk_path)
                            self.logger.debug(f"Chunk {chunk_number} idêntico já existe")
                        else:
                            os.replace(temp_chunk_path, chunk_path)
                            self.logger.debug(f"Chunk {chunk_number} substituído (hash diferente)")
                    else:
                        os.replace(temp_chunk_path, chunk_path)

                except Exception as e:
                    try:
                        if os.path.exists(temp_chunk_path):
                            os.remove(temp_chunk_path)
                    except:
                        pass
                    raise e

                max_db_retries = 3
                for db_attempt in range(max_db_retries):
                    try:
                        self.db.refresh(upload)
                        current_uploaded_chunks = self._parse_uploaded_chunks(upload.uploaded_chunks)

                        if chunk_number not in current_uploaded_chunks:
                            current_uploaded_chunks.append(chunk_number)
                            current_uploaded_chunks.sort()
                            upload.uploaded_chunks = ",".join(map(str, current_uploaded_chunks))
                            upload.updated_at = datetime.now(timezone.utc)

                        self.db.commit()

                        progress = len(current_uploaded_chunks) / upload.total_chunks * 100
                        self.logger.debug(f"Chunk {chunk_number} salvo. Progresso: {progress:.1f}%")

                        return ChunkUploadResponse(
                            chunk_number=chunk_number,
                            received=True,
                            upload_progress=progress,
                            uploaded_chunks=current_uploaded_chunks
                        )

                    except SQLAlchemyError as e:
                        self.db.rollback()
                        if db_attempt == max_db_retries - 1:
                            try:
                                if os.path.exists(chunk_path):
                                    os.remove(chunk_path)
                            except:
                                pass
                            raise Exception(f"Erro ao atualizar banco após {max_db_retries} tentativas: {e}")

                        time.sleep(0.1 * (db_attempt + 1))

            finally:
                try:
                    if os.path.exists(chunk_lock_path):
                        os.remove(chunk_lock_path)
                except:
                    pass

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Erro de banco de dados: {e}")

    def complete_upload(self, upload_id: str, actor, client_resource_permission) -> ChunkedUploadComplete:
        self.logger.info(f"Iniciando finalização do upload: {upload_id}")

        upload = self.db.query(ChunkedUpload).filter(
            ChunkedUpload.upload_id == upload_id
        ).first()

        if not upload:
            raise HTTPException(status_code=404, detail="Upload não encontrado")

        if upload.is_completed:
            self.logger.info(f"Upload {upload_id} já foi completado anteriormente")
            return ChunkedUploadComplete(
                upload_id=upload_id,
                final_file_id=upload.final_file_id,
                message="Upload já foi completado"
            )

        uploaded_chunks_db = self._parse_uploaded_chunks(upload.uploaded_chunks)
        uploaded_chunks_disk = self._verify_chunks_on_disk(upload_id, upload.total_chunks)

        verified_chunks = []
        chunk_dir = os.path.join(self.temp_dir, upload.upload_id)

        for chunk_num in uploaded_chunks_disk:
            chunk_path = os.path.join(chunk_dir, f"chunk_{chunk_num:06d}")
            try:
                if os.path.exists(chunk_path) and os.path.getsize(chunk_path) > 0:
                    verified_chunks.append(chunk_num)
            except OSError:
                self.logger.warning(f"Erro ao verificar chunk {chunk_num}")
                continue

        verified_chunks.sort()
        expected_chunks = list(range(1, upload.total_chunks + 1))
        missing_chunks = sorted(set(expected_chunks) - set(verified_chunks))

        if missing_chunks:
            try:
                upload.uploaded_chunks = ",".join(map(str, verified_chunks))
                self.db.commit()
                self.logger.warning(f"Upload {upload_id} com chunks faltando: {missing_chunks}")
            except SQLAlchemyError:
                self.db.rollback()

            raise HTTPException(
                status_code=400,
                detail=f"Chunks faltando: {missing_chunks}"
            )

        try:
            final_file = self._merge_chunks(upload)
            upload.is_completed = True
            upload.final_file_id = final_file.id
            upload.updated_at = datetime.now(timezone.utc)
            self.db.commit()

            try:
                self._cleanup_chunks(upload_id)
            except Exception as e:
                self.logger.warning(f"Erro ao limpar chunks: {e}")

            cache.invalidate("files")
            cache.invalidate("dashboard")

            self.logger.info(f"Upload {upload_id} completado com sucesso. Arquivo: {final_file.id}")

            return ChunkedUploadComplete(
                upload_id=upload_id,
                final_file_id=final_file.id,
                message="Upload completado com sucesso"
            )

        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erro ao finalizar upload {upload_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Erro ao finalizar upload: {str(e)}")

    def _verify_chunks_on_disk(self, upload_id: str, total_chunks: int) -> List[int]:
        chunk_dir = os.path.join(self.temp_dir, upload_id)
        existing_chunks = []

        if not os.path.exists(chunk_dir):
            self.logger.warning(f"Diretório de chunks não existe: {chunk_dir}")
            return existing_chunks

        try:
            for chunk_num in range(1, total_chunks + 1):
                chunk_path = os.path.join(chunk_dir, f"chunk_{chunk_num:06d}")
                if os.path.exists(chunk_path):
                    try:
                        size = os.path.getsize(chunk_path)
                        if size > 0:
                            existing_chunks.append(chunk_num)
                        else:
                            self.logger.warning(f"Chunk {chunk_num} está vazio")
                    except OSError as e:
                        self.logger.warning(f"Erro ao verificar chunk {chunk_num}: {e}")
        except Exception as e:
            self.logger.error(f"Erro ao verificar chunks no disco: {e}")

        return existing_chunks

    def retry_missing_chunks(self, upload_id: str) -> ChunkedUploadStatus:
        upload = self.db.query(ChunkedUpload).filter(
            ChunkedUpload.upload_id == upload_id
        ).first()

        if not upload:
            raise HTTPException(status_code=404, detail="Upload não encontrado")

        if upload.is_completed:
            raise HTTPException(status_code=400, detail="Upload já foi completado")

        uploaded_chunks_db = self._parse_uploaded_chunks(upload.uploaded_chunks)
        uploaded_chunks_disk = self._verify_chunks_on_disk(upload_id, upload.total_chunks)

        verified_chunks = list(set(uploaded_chunks_db) & set(uploaded_chunks_disk))
        verified_chunks.sort()

        if set(verified_chunks) != set(uploaded_chunks_db):
            upload.uploaded_chunks = ",".join(map(str, verified_chunks))
            self.db.commit()

        expected_chunks = list(range(1, upload.total_chunks + 1))
        missing_chunks = sorted(set(expected_chunks) - set(verified_chunks))

        progress = len(verified_chunks) / upload.total_chunks * 100

        return ChunkedUploadStatus(
            upload_id=upload_id,
            filename=upload.filename,
            total_chunks=upload.total_chunks,
            uploaded_chunks=verified_chunks,
            missing_chunks=missing_chunks,
            progress=progress,
            is_completed=upload.is_completed,
            final_file_id=upload.final_file_id,
            created_at=upload.created_at,
            expires_at=upload.expires_at
        )

    def _merge_chunks(self, upload: ChunkedUpload) -> File:
        import hashlib

        category = FileCategory.document
        if upload.category:
            try:
                category = FileCategory(upload.category)
            except ValueError:
                pass
        else:
            mime = upload.mime_type or ""
            if mime.startswith("image/"):
                category = FileCategory.image
            elif mime.startswith("video/"):
                category = FileCategory.video

        safe_original = self.sanitize_filename(upload.filename)
        stored_name, dest_path = self._build_storage_path(safe_original, category)

        chunk_dir = os.path.join(self.temp_dir, upload.upload_id)
        sha256_hash = hashlib.sha256()

        with open(dest_path, "wb") as output_file:
            for chunk_num in range(1, upload.total_chunks + 1):
                chunk_path = os.path.join(chunk_dir, f"chunk_{chunk_num:06d}")
                if not os.path.exists(chunk_path):
                    raise HTTPException(status_code=500, detail=f"Chunk {chunk_num} não encontrado")

                with open(chunk_path, "rb") as chunk_file:
                    while True:
                        data = chunk_file.read(8192)
                        if not data:
                            break
                        output_file.write(data)
                        sha256_hash.update(data)

        if upload.file_checksum:
            calculated_checksum = sha256_hash.hexdigest()
            if calculated_checksum != upload.file_checksum:
                try:
                    os.remove(dest_path)
                except:
                    pass
                raise HTTPException(
                    status_code=400,
                    detail=f"Checksum inválido. Esperado: {upload.file_checksum}, Calculado: {calculated_checksum}"
                )
            self.logger.info(f"Checksum validado com sucesso para upload {upload.upload_id}")

        file_model = File(
            original_name=safe_original,
            stored_name=stored_name,
            path=dest_path,
            size=upload.total_size,
            mime_type=upload.mime_type or "application/octet-stream",
            category=category,
            description=upload.description,
            project_id=upload.project_id,
            client_id=upload.client_id,
            stage_id=upload.stage_id,
            uploaded_by_id=upload.uploaded_by_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        self.db.add(file_model)
        self.db.commit()

        return file_model

    def _parse_uploaded_chunks(self, chunks_str: str) -> List[int]:
        if not chunks_str:
            return []
        return [int(x) for x in chunks_str.split(",") if x.strip()]

    def _cleanup_chunks(self, upload_id: str):
        chunk_dir = os.path.join(self.temp_dir, upload_id)
        try:
            if os.path.exists(chunk_dir):
                for file in os.listdir(chunk_dir):
                    file_path = os.path.join(chunk_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                os.rmdir(chunk_dir)
        except Exception as e:
            self.logger.error(f"Erro ao limpar chunks do upload {upload_id}: {e}")

    def cancel_upload(self, upload_id: str) -> dict:
        self.logger.info(f"Cancelando upload: {upload_id}")

        upload = self.db.query(ChunkedUpload).filter(
            ChunkedUpload.upload_id == upload_id
        ).first()

        if not upload:
            raise HTTPException(status_code=404, detail="Upload não encontrado")

        if upload.is_completed:
            raise HTTPException(status_code=400, detail="Não é possível cancelar upload já completado")

        try:
            self._cleanup_chunks(upload_id)
            self.db.delete(upload)
            self.db.commit()

            self.logger.info(f"Upload {upload_id} cancelado com sucesso")
            return {"message": "Upload cancelado com sucesso"}

        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erro ao cancelar upload {upload_id}: {e}")
            raise HTTPException(status_code=500, detail="Erro ao cancelar upload")

    def get_upload_status(self, upload_id: str) -> ChunkedUploadStatus:
        upload = self.db.query(ChunkedUpload).filter(
            ChunkedUpload.upload_id == upload_id
        ).first()

        if not upload:
            raise HTTPException(status_code=404, detail="Upload não encontrado")

        uploaded_chunks = self._parse_uploaded_chunks(upload.uploaded_chunks)
        progress = len(uploaded_chunks) / upload.total_chunks * 100

        chunks_on_disk = self._verify_chunks_on_disk(upload_id, upload.total_chunks)
        verified_chunks = list(set(uploaded_chunks) & set(chunks_on_disk))

        expected_chunks = list(range(1, upload.total_chunks + 1))
        missing_chunks = sorted(set(expected_chunks) - set(verified_chunks))

        return ChunkedUploadStatus(
            upload_id=upload_id,
            filename=upload.filename,
            total_chunks=upload.total_chunks,
            uploaded_chunks=verified_chunks,
            missing_chunks=missing_chunks,
            progress=len(verified_chunks) / upload.total_chunks * 100,
            is_completed=upload.is_completed,
            final_file_id=upload.final_file_id,
            created_at=upload.created_at,
            expires_at=upload.expires_at
        )

    def cleanup_expired_uploads(self) -> dict:
        try:
            expired_uploads = self.db.query(ChunkedUpload).filter(
                ChunkedUpload.expires_at < datetime.now(timezone.utc),
                ChunkedUpload.is_completed == False
            ).all()

            cleaned_count = 0
            total_size_cleaned = 0

            for upload in expired_uploads:
                try:
                    chunk_dir = os.path.join(self.temp_dir, upload.upload_id)
                    if os.path.exists(chunk_dir):
                        for file in os.listdir(chunk_dir):
                            file_path = os.path.join(chunk_dir, file)
                            if os.path.isfile(file_path):
                                total_size_cleaned += os.path.getsize(file_path)

                    self._cleanup_chunks(upload.upload_id)
                    self.db.delete(upload)
                    cleaned_count += 1
                except Exception as e:
                    self.logger.error(f"Erro ao limpar upload expirado {upload.upload_id}: {e}")
                    continue

            self.db.commit()

            result = {
                "message": "Limpeza concluída",
                "uploads_removed": cleaned_count,
                "total_uploads_expired": len(expired_uploads),
                "space_freed_bytes": total_size_cleaned,
                "space_freed_mb": round(total_size_cleaned / (1024 * 1024), 2)
            }

            self.logger.info(f"Limpeza concluída: {result}")
            return result

        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erro na limpeza de uploads expirados: {e}")
            raise HTTPException(status_code=500, detail="Erro na limpeza de uploads expirados")
