from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, validator


class StageTypeBase(BaseModel):
    name: str
    description: Optional[str] = None
    scope: Optional[dict] = None
    default_duration_days: Optional[int] = None
    is_active: bool = True


class StageTypeCreate(StageTypeBase):

    @validator('scope')
    def validate_scope(cls, v):
        if v is None:
            return v

        if not isinstance(v, dict):
            raise ValueError('Escopo deve ser um objeto JSON válido')

        # Validar estrutura do escopo
        for field_name, field_config in v.items():
            if not isinstance(field_config, dict):
                raise ValueError(f'Configuração do campo "{field_name}" deve ser um objeto')

            required_keys = {'type', 'required', 'label'}
            if not required_keys.issubset(field_config.keys()):
                raise ValueError(f'Campo "{field_name}" deve conter: type, required, label')

            valid_types = {'string', 'text', 'number', 'date', 'boolean', 'array'}
            if field_config['type'] not in valid_types:
                raise ValueError(f'Tipo "{field_config["type"]}" inválido para campo "{field_name}". Tipos válidos: {valid_types}')

            if not isinstance(field_config['required'], bool):
                raise ValueError(f'Campo "required" do campo "{field_name}" deve ser boolean')

            if not isinstance(field_config['label'], str):
                raise ValueError(f'Campo "label" do campo "{field_name}" deve ser string')

        return v


class StageTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    scope: Optional[dict] = None
    default_duration_days: Optional[int] = None
    is_active: Optional[bool] = None

    @validator('scope')
    def validate_scope(cls, v):
        if v is None:
            return v

        if not isinstance(v, dict):
            raise ValueError('Escopo deve ser um objeto JSON válido')

        for field_name, field_config in v.items():
            if not isinstance(field_config, dict):
                raise ValueError(f'Configuração do campo "{field_name}" deve ser um objeto')

            required_keys = {'type', 'required', 'label'}
            if not required_keys.issubset(field_config.keys()):
                raise ValueError(f'Campo "{field_name}" deve conter: type, required, label')

            valid_types = {'string', 'text', 'number', 'date', 'boolean', 'array'}
            if field_config['type'] not in valid_types:
                raise ValueError(f'Tipo "{field_config["type"]}" inválido para campo "{field_name}". Tipos válidos: {valid_types}')

            if not isinstance(field_config['required'], bool):
                raise ValueError(f'Campo "required" do campo "{field_name}" deve ser boolean')

            if not isinstance(field_config['label'], str):
                raise ValueError(f'Campo "label" do campo "{field_name}" deve ser string')

        return v


class StageTypeRead(StageTypeBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedStageTypes(BaseModel):
    total: int
    count: int
    offset: int
    limit: int
    items: List[StageTypeRead]
