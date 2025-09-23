import json
import os
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "" #"/api/v1"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"

    # Ambiente
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = []

    # Cookies/Sessão
    COOKIE_SECURE: bool | None = None
    COOKIE_SAMESITE: str = "lax"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            if v.startswith("["):
                return json.loads(v)
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(v)

    @field_validator("COOKIE_SECURE", mode="before")
    @classmethod
    def default_cookie_secure_from_env(cls, v, info):
        # Se COOKIE_SECURE vier definido explicitamente, respeita
        if v is not None:
            return v
        # Caso contrário, deriva de ENVIRONMENT (ou variável de ambiente ENVIRONMENT)
        data = getattr(info, 'data', {}) or {}
        env = (data.get('ENVIRONMENT') or os.getenv('ENVIRONMENT') or 'development').strip().lower()
        return env in ("prod", "production")

    # File Storage
    UPLOAD_DIR: str = "app/storage/uploads"
    MAX_FILE_SIZE: int = 1 * 1024 * 1024 * 1024  # 1GB
    ALLOWED_EXTENSIONS: List[str] = [
        ".jpg", ".jpeg", ".png", ".gif", ".webp", ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".dwg", ".dxf", ".txt", ".zip", ".rar",
        # Vídeo
        ".mp4", ".mov", ".avi", ".mkv", ".webm",
        # Renders/3D
        ".blend", ".fbx", ".obj", ".gltf", ".glb", ".3ds", ".stl", ".dae", ".max", ".c4d",
        # Outros
        ".ppt", ".pptx", ".csv", ".svg", ".heic", ".tif", ".tiff"
    ]

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"


settings = Settings()
