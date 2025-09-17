from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from ..api.dependencies import get_db, get_current_actor_factory
from ..schemas.client import ClientCreate, ClientUpdate, ClientRead, PaginatedClients
from ..services.client_service import ClientService

router = APIRouter()

@router.get("", response_model=PaginatedClients)
async def get_clients(
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_actor_factory(["admin"])),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_by: str = Query("created_at"),
    order_dir: str = Query("desc", pattern="^(asc|desc)$"),
    search: str = Query(None),
    is_active: bool = Query(None),
):
    service = ClientService(db)
    return await run_in_threadpool(
        service.get_clients,
        limit, offset, order_by, order_dir, search, is_active
    )

@router.get("/{client_id}", response_model=ClientRead)
async def get_client(client_id: str, db: Session = Depends(get_db), actor = Depends(get_current_actor_factory())):
    service = ClientService(db)
    return await run_in_threadpool(service.get_client, client_id, actor)

@router.post("", response_model=ClientRead)
async def create_client(client_data: ClientCreate, db: Session = Depends(get_db), admin_user = Depends(get_current_actor_factory(["admin"]))):
    service = ClientService(db)
    return await run_in_threadpool(service.create_client, client_data)

@router.put("/{client_id}", response_model=ClientRead)
async def update_client(client_id: str, client_data: ClientUpdate, db: Session = Depends(get_db), admin_user = Depends(get_current_actor_factory(["admin"]))):
    service = ClientService(db)
    return await run_in_threadpool(service.update_client, client_id, client_data)

@router.delete("/{client_id}")
async def delete_client(client_id: str, db: Session = Depends(get_db), admin_user = Depends(get_current_actor_factory(["admin"]))):
    service = ClientService(db)
    return await run_in_threadpool(service.delete_client, client_id)

@router.post("/{client_id}/reset-password")
async def reset_client_password(client_id: str, db: Session = Depends(get_db), admin_user = Depends(get_current_actor_factory(["admin"]))):
    service = ClientService(db)
    return await run_in_threadpool(service.reset_client_password, client_id)

class PasswordSetRequest(BaseModel):
    password: str

@router.post("/{client_id}/set-password")
async def set_client_password(client_id: str, payload: PasswordSetRequest, db: Session = Depends(get_db), admin_user = Depends(get_current_actor_factory(["admin"]))):
    service = ClientService(db)
    return await run_in_threadpool(service.set_client_password, client_id, payload.password)
