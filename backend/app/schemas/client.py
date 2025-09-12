import enum
from datetime import datetime, date
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, EmailStr

if TYPE_CHECKING:
    from .project import ProjectRead


class DocumentType(str, enum.Enum):
    cpf = "cpf"
    cnpj = "cnpj"


class ClientBase(BaseModel):
    name: str
    document: str
    document_type: DocumentType
    rg_ie: Optional[str] = None
    birth_date: Optional[date] = None
    email: EmailStr
    secondary_email: Optional[EmailStr] = None
    phone: str
    mobile: Optional[str] = None
    whatsapp: Optional[str] = None
    address: Optional[dict] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = True


class ClientCreate(ClientBase):
    password: Optional[str] = None


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    document: Optional[str] = None
    document_type: Optional[DocumentType] = None
    rg_ie: Optional[str] = None
    birth_date: Optional[date] = None
    email: Optional[EmailStr] = None
    secondary_email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    whatsapp: Optional[str] = None
    address: Optional[dict] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class ClientBasicRead(BaseModel):
    id: UUID
    name: str
    document: str
    document_type: DocumentType
    email: EmailStr
    phone: str
    is_active: Optional[bool] = True

    class Config:
        from_attributes = True


class ClientRead(ClientBase):
    id: UUID
    first_access: bool
    created_at: datetime
    updated_at: datetime
    projects: Optional[List["ProjectRead"]] = None
    model_config = {"from_attributes": True}


class PaginatedClients(BaseModel):
    total: int
    count: int
    offset: int
    limit: int
    items: List[ClientRead]
