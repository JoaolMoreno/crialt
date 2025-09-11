from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..api.dependencies import get_db, get_current_actor, get_current_actor_factory
from ..models.client import Client
from ..schemas.client import ClientCreate, ClientUpdate, ClientRead
from ..services.auth_service import AuthService
from ..core.security import get_password_hash
from pydantic import BaseModel

router = APIRouter()

def serialize_client(client):
    data = client.__dict__.copy()
    if hasattr(client, "projects") and client.projects:
        data["projects"] = [p.id for p in client.projects]
    else:
        data["projects"] = []
    return ClientRead.model_validate(data)

@router.get("", response_model=List[ClientRead])
def get_clients(db: Session = Depends(get_db), admin_user = Depends(get_current_actor_factory(["admin"]))):
    clients = db.query(Client).all()
    return [serialize_client(client) for client in clients]

@router.get("/{client_id}", response_model=ClientRead)
def get_client(client_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor_factory())):
    client = db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    if hasattr(actor, "role") and getattr(actor, "role", None) == "admin":
        return serialize_client(client)
    if hasattr(actor, "id") and str(actor.id) == str(client.id):
        return serialize_client(client)
    raise HTTPException(status_code=403, detail="Acesso negado")

@router.post("", response_model=ClientRead)
def create_client(client_data: ClientCreate, db: Session = Depends(get_db), admin_user = Depends(get_current_actor_factory(["admin"]))):
    existing_email = db.query(Client).filter(Client.email == client_data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    existing_doc = db.query(Client).filter(Client.document == client_data.document).first()
    if existing_doc:
        raise HTTPException(status_code=400, detail="Documento já cadastrado")
    client = Client(
        name=client_data.name,
        document=client_data.document,
        document_type=client_data.document_type,
        rg_ie=client_data.rg_ie,
        birth_date=client_data.birth_date,
        email=str(client_data.email),
        secondary_email=str(client_data.secondary_email) if client_data.secondary_email else None,
        phone=client_data.phone,
        mobile=client_data.mobile,
        whatsapp=client_data.whatsapp,
        address=client_data.address,
        notes=client_data.notes,
        is_active=client_data.is_active if client_data.is_active is not None else True,
        password_hash=get_password_hash(client_data.password) if client_data.password else None,
        first_access=True
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return serialize_client(client)

@router.put("/{client_id}", response_model=ClientRead)
def update_client(client_id: str, client_data: ClientUpdate, db: Session = Depends(get_db), admin_user = Depends(get_current_actor_factory(["admin"]))):
    client = db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    update_data = client_data.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        client.password_hash = get_password_hash(update_data["password"])
        update_data.pop("password")
    for field, value in update_data.items():
        setattr(client, field, value)
    db.commit()
    db.refresh(client)
    return serialize_client(client)

@router.delete("/{client_id}")
def delete_client(client_id: str, db: Session = Depends(get_db), admin_user = Depends(get_current_actor_factory(["admin"]))):
    client = db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    client.is_active = False  # Soft delete
    db.commit()
    return {"message": "Cliente desativado com sucesso"}

@router.post("/{client_id}/reset-password")
def reset_client_password(client_id: str, db: Session = Depends(get_db), admin_user = Depends(get_current_actor_factory(["admin"]))):
    client = db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    auth = AuthService(db)
    new_password = auth.reset_client_password(client)
    return {"new_password": new_password}

class PasswordSetRequest(BaseModel):
    password: str

@router.post("/{client_id}/set-password")
def set_client_password(client_id: str, payload: PasswordSetRequest, db: Session = Depends(get_db), admin_user = Depends(get_current_actor_factory(["admin"]))):
    client = db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    client.password_hash = get_password_hash(payload.password)
    db.commit()
    db.refresh(client)
    return {"message": "Senha definida com sucesso"}
