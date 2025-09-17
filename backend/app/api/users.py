from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from starlette.concurrency import run_in_threadpool

from ..api.dependencies import get_db, get_current_user, get_current_actor_factory
from ..models import User
from ..schemas.user import UserRead, UserCreate, UserUpdate
from ..services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserRead)
async def get_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = UserService(db)
    return await run_in_threadpool(service.get_me, user)


@router.get("", response_model=List[UserRead])
async def get_users(db: Session = Depends(get_db), admin_user: User = Depends(get_current_actor_factory(["admin"]))):
    service = UserService(db)
    return await run_in_threadpool(service.get_users)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: str, db: Session = Depends(get_db), admin_user: User = Depends(get_current_actor_factory(["admin"]))):
    service = UserService(db)
    return await run_in_threadpool(service.get_user, user_id)


@router.post("", response_model=UserRead)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db), admin_user: User = Depends(get_current_actor_factory(["admin"]))):
    service = UserService(db)
    return await run_in_threadpool(service.create_user, user_data)


@router.put("/{user_id}", response_model=UserRead)
async def update_user(user_id: str, user_data: UserUpdate, db: Session = Depends(get_db), admin_user: User = Depends(get_current_actor_factory(["admin"]))):
    service = UserService(db)
    return await run_in_threadpool(service.update_user, user_id, user_data)


@router.delete("/{user_id}")
async def delete_user(user_id: str, db: Session = Depends(get_db), admin_user: User = Depends(get_current_actor_factory(["admin"]))):
    service = UserService(db)
    return await run_in_threadpool(service.delete_user, user_id)
