from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class ChunkedUploadInitiate(BaseModel):
    filename: str = Field(..., description="Nome do arquivo original")
    total_chunks: int = Field(..., gt=0, description="Número total de chunks")
    chunk_size: int = Field(..., gt=0, description="Tamanho de cada chunk em bytes")
    total_size: int = Field(..., gt=0, description="Tamanho total do arquivo em bytes")
    file_checksum: Optional[str] = Field(None, description="Checksum SHA-256 do arquivo completo")
    mime_type: Optional[str] = None
    category: Optional[str] = None
    project_id: Optional[UUID] = None
    client_id: Optional[UUID] = None
    stage_id: Optional[UUID] = None
    description: Optional[str] = None


class ChunkedUploadResponse(BaseModel):
    upload_id: str = Field(..., description="ID único do upload")
    expires_at: datetime = Field(..., description="Data de expiração do upload")
    uploaded_chunks: List[int] = Field(default=[], description="Lista de chunks já recebidos")


class ChunkUploadResponse(BaseModel):
    chunk_number: int
    received: bool
    upload_progress: float = Field(..., ge=0.0, le=100.0, description="Progresso em porcentagem")
    uploaded_chunks: List[int]


class ChunkedUploadStatus(BaseModel):
    upload_id: str
    filename: str
    total_chunks: int
    uploaded_chunks: List[int]
    missing_chunks: Optional[List[int]] = Field(default=[], description="Lista de chunks faltando para retry")
    progress: float = Field(..., ge=0.0, le=100.0)
    is_completed: bool
    final_file_id: Optional[UUID] = None
    created_at: datetime
    expires_at: datetime


class ChunkedUploadComplete(BaseModel):
    upload_id: str
    final_file_id: UUID
    message: str
