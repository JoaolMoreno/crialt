import enum
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserRole(str, enum.Enum):
    admin = "admin"
    architect = "architect"
    assistant = "assistant"

class UserBase(BaseModel):
    name: str
    email: EmailStr
    username: str
    role: UserRole = UserRole.architect
    avatar: Optional[str] = None
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    role: Optional[UserRole] = None
    avatar: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class UserRead(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        orm_mode = True
