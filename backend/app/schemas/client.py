from typing import Optional, List
from uuid import UUID
from datetime import datetime, date
from pydantic import BaseModel, EmailStr
import enum

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

class ClientRead(ClientBase):
    id: UUID
    first_access: bool
    created_at: datetime
    updated_at: datetime
    projects: Optional[List[UUID]] = None
    documents: Optional[List[UUID]] = None

    class Config:
        orm_mode = True
