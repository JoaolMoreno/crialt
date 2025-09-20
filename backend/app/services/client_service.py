from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from ..models.client import Client
from ..schemas.client import ClientCreate, ClientUpdate, ClientRead, PaginatedClients
from ..schemas.project import ProjectRead, serialize_project
from ..core.security import get_password_hash
from ..services.auth_service import AuthService
from ..utils.cache import cache
import logging


class ClientService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)

    def serialize_client(self, client):
        data = client.__dict__.copy()
        if hasattr(client, "projects") and client.projects:
            data["projects"] = [ProjectRead.model_validate(serialize_project(p)) for p in client.projects]
        else:
            data["projects"] = []
        return ClientRead.model_validate(data)

    def get_clients(self, limit: int, offset: int, order_by: str, order_dir: str, search: Optional[str], is_active: Optional[bool]) -> PaginatedClients:
        cache_params = {
            "limit": limit,
            "offset": offset,
            "order_by": order_by,
            "order_dir": order_dir,
            "search": search,
            "is_active": is_active
        }
        cached = cache.get("clients", cache_params)
        if cached:
            self.logger.info(f"[CACHE] get_clients: params={cache_params}")
            return cached
        self.logger.info(f"[DB] get_clients: params={cache_params}")
        query = self.db.query(Client)
        if search:
            like_pattern = f"%{search}%"
            query = query.filter(
                (Client.name.ilike(like_pattern)) |
                (Client.document.ilike(like_pattern)) |
                (Client.email.ilike(like_pattern))
            )
        if is_active is not None:
            query = query.filter(Client.is_active == is_active)
        if hasattr(Client, order_by):
            order_col = getattr(Client, order_by)
            if order_dir == "desc":
                order_col = order_col.desc()
            else:
                order_col = order_col.asc()
            query = query.order_by(order_col)
        total = query.count()
        items = query.offset(offset).limit(limit).all()
        result = [self.serialize_client(client) for client in items]
        paginated = PaginatedClients(
            total=total,
            count=len(result),
            offset=offset,
            limit=limit,
            items=result
        )
        cache.set("clients", cache_params, paginated)
        return paginated

    def get_client(self, client_id: str, actor: Any) -> ClientRead:
        client = self.db.get(Client, client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Cliente não foi encontrado.")
        if hasattr(actor, "role") and getattr(actor, "role", None) == "admin":
            return self.serialize_client(client)
        if hasattr(actor, "id") and str(actor.id) == str(client.id):
            return self.serialize_client(client)
        raise HTTPException(status_code=403, detail="Você não tem permissão para acessar este recurso.")

    def create_client(self, client_data: ClientCreate) -> ClientRead:
        existing_email = self.db.query(Client).filter(Client.email == client_data.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Já existe um cliente com este e-mail.")
        existing_doc = self.db.query(Client).filter(Client.document == client_data.document).first()
        if existing_doc:
            raise HTTPException(status_code=400, detail="Já existe um cliente com este documento.")
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
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        cache.invalidate("clients")
        cache.invalidate("dashboard")
        return self.serialize_client(client)

    def update_client(self, client_id: str, client_data: ClientUpdate) -> ClientRead:
        client = self.db.get(Client, client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Cliente não foi encontrado.")
        update_data = client_data.model_dump(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            client.password_hash = get_password_hash(update_data["password"])
            update_data.pop("password")
        for field, value in update_data.items():
            setattr(client, field, value)
        self.db.commit()
        self.db.refresh(client)
        cache.invalidate("clients")
        cache.invalidate("dashboard")
        return self.serialize_client(client)

    def delete_client(self, client_id: str) -> Dict[str, str]:
        client = self.db.get(Client, client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Cliente não foi encontrado")
        client.is_active = False  # Soft delete
        self.db.commit()
        cache.invalidate("clients")
        cache.invalidate("dashboard")
        return {"message": "Cliente desativado com sucesso"}

    def reset_client_password(self, client_id: str) -> Dict[str, str]:
        client = self.db.get(Client, client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        auth = AuthService(self.db)
        new_password = auth.reset_client_password(client)
        return {"new_password": new_password}

    def set_client_password(self, client_id: str, password: str) -> Dict[str, str]:
        client = self.db.get(Client, client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        client.password_hash = get_password_hash(password)
        self.db.commit()
        self.db.refresh(client)
        return {"message": "Senha definida com sucesso"}
