"""
Schemas Module
Contém todos os schemas Pydantic para validação de dados
"""

# Client schemas
from .client import DocumentType, ClientBase, ClientCreate, ClientUpdate, ClientRead
# User schemas
from .user import UserRole, UserBase, UserCreate, UserUpdate, UserRead
# Project schemas
from .project import ProjectStatus, ProjectBase, ProjectCreate, ProjectUpdate, ProjectRead
# Stage Type schemas
from .stage_type import StageTypeBase, StageTypeCreate, StageTypeUpdate, StageTypeRead
# Stage schemas
from .stage import StageStatus, StageBase, StageCreate, StageUpdate
# Task schemas
from .task import TaskStatus, TaskPriority, TaskBase, TaskCreate, TaskUpdate, TaskRead
# File schemas
from .file import FileCategory, FileBase, FileCreate, FileUpdate, FileRead

__all__ = [
    # Client
    "DocumentType", "ClientBase", "ClientCreate", "ClientUpdate", "ClientRead",
    # User
    "UserRole", "UserBase", "UserCreate", "UserUpdate", "UserRead",
    # Project
    "ProjectStatus", "ProjectBase", "ProjectCreate", "ProjectUpdate", "ProjectRead",
    # Stage Type
    "StageTypeBase", "StageTypeCreate", "StageTypeUpdate", "StageTypeRead",
    # Stage
    "StageStatus", "StageBase", "StageCreate", "StageUpdate",
    # Task
    "TaskStatus", "TaskPriority", "TaskBase", "TaskCreate", "TaskUpdate", "TaskRead",
    # File
    "FileCategory", "FileBase", "FileCreate", "FileUpdate", "FileRead",
]
