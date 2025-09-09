from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import get_db, get_current_user, admin_required
from app.models import User
from app.schemas.user import UserRead, UserCreate, UserUpdate
from app.core.security import get_password_hash

router = APIRouter()


@router.get("/me", response_model=UserRead)
def get_me(user: User = Depends(get_current_user)):
    return user


@router.get("/", response_model=List[UserRead])
def get_users(db: Session = Depends(get_db), admin_user: User = Depends(admin_required)):
    users = db.query(User).all()
    return users


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: str, db: Session = Depends(get_db), admin_user: User = Depends(admin_required)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user


@router.post("/", response_model=UserRead)
def create_user(user_data: UserCreate,
                db: Session = Depends(get_db),
                admin_user: User = Depends(admin_required)
                ):
    print("Create user called")
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    user = User(
        name=user_data.name,
        username=user_data.username,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role,
        avatar=user_data.avatar,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}", response_model=UserRead)
def update_user(user_id: str, user_data: UserUpdate, db: Session = Depends(get_db), admin_user: User = Depends(admin_required)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    update_data = user_data.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["password"] = get_password_hash(update_data["password"])

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db), admin_user: User = Depends(admin_required)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    user.is_active = False  # Soft delete
    db.commit()
    return {"message": "Usuário desativado com sucesso"}
