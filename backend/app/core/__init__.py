"""
Core Module
Contém configurações, banco de dados, segurança e exceções
"""

from .config import Settings
from .database import SessionLocal, engine

settings = Settings()
__all__ = [
    "settings",
    "SessionLocal",
    "engine",
]
