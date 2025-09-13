from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..api.dependencies import get_db, get_current_actor_factory
from ..api.projects import serialize_project
from ..core.security import get_password_hash
from ..models.client import Client
from ..schemas.client import ClientCreate, ClientUpdate, ClientRead, PaginatedClients
from ..schemas.project import ProjectRead
from ..services.auth_service import AuthService
from ..utils.cache import cache

router = APIRouter()

def serialize_client(client):
    data = client.__dict__.copy()
    if hasattr(client, "projects") and client.projects:
        data["projects"] = [ProjectRead.model_validate(serialize_project(p)) for p in client.projects]
    else:
        data["projects"] = []
    return ClientRead.model_validate(data)

@router.get("", response_model=PaginatedClients)
def get_clients(
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_actor_factory(["admin"])),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_by: str = Query("created_at"),
    order_dir: str = Query("desc", pattern="^(asc|desc)$"),
    name: str = Query(None),
    document: str = Query(None),
    email: str = Query(None),
    is_active: bool = Query(None),
):
    cache_params = {
        "limit": limit,
        "offset": offset,
        "order_by": order_by,
        "order_dir": order_dir,
        "name": name,
        "document": document,
        "email": email,
        "is_active": is_active
    }
    cached = cache.get("clients", cache_params)
    if cached:
        return cached
    query = db.query(Client)
    if name:
        query = query.filter(Client.name.ilike(f"%{name}%"))
    if document:
        query = query.filter(Client.document == document)
    if email:
        query = query.filter(Client.email == email)
    if is_active is not None:
        query = query.filter(Client.is_active == is_active)
    # Ordenação
    if hasattr(Client, order_by):
        order_col = getattr(Client, order_by)
        if order_dir == "desc":
            order_col = order_col.desc()
        else:
            order_col = order_col.asc()
        query = query.order_by(order_col)
    total = query.count()
    items = query.offset(offset).limit(limit).all()
    result = [serialize_client(client) for client in items]
    paginated = PaginatedClients(
        total=total,
        count=len(result),
        offset=offset,
        limit=limit,
        items=result
    )
    cache.set("clients", cache_params, paginated)
    return paginated

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
    cache.invalidate("clients")
    cache.invalidate("dashboard")
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
    cache.invalidate("clients")
    cache.invalidate("dashboard")
    return serialize_client(client)

@router.delete("/{client_id}")
def delete_client(client_id: str, db: Session = Depends(get_db), admin_user = Depends(get_current_actor_factory(["admin"]))):
    client = db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    client.is_active = False  # Soft delete
    db.commit()
    cache.invalidate("clients")
    cache.invalidate("dashboard")
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
