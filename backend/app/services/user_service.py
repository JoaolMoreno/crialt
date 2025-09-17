from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..models import User
from ..schemas.user import UserRead, UserCreate, UserUpdate
from ..core.security import get_password_hash
from ..utils.cache import cache
import logging

class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)

    def get_me(self, user: User) -> UserRead:
        return UserRead.model_validate(user)

    def get_users(self) -> List[UserRead]:
        cached = cache.get("users", {})
        if cached:
            self.logger.info(f"[CACHE] get_users: params={{}}")
            return cached
        self.logger.info(f"[DB] get_users: params={{}}")
        users = self.db.query(User).all()
        result = [UserRead.model_validate(u) for u in users]
        cache.set("users", {}, result)
        return result

    def get_user(self, user_id: str) -> UserRead:
        user = self.db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return UserRead.model_validate(user)

    def create_user(self, user_data: UserCreate) -> UserRead:
        existing = self.db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        user = User(
            name=user_data.name,
            username=user_data.username,
            email=str(user_data.email),
            password_hash=get_password_hash(user_data.password),
            role=user_data.role,
            avatar=user_data.avatar,
            is_active=True
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        cache.invalidate("users")
        cache.invalidate("dashboard")
        return UserRead.model_validate(user)

    def update_user(self, user_id: str, user_data: UserUpdate) -> UserRead:
        user = self.db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        update_data = user_data.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["password_hash"] = get_password_hash(update_data.pop("password"))
        for field, value in update_data.items():
            setattr(user, field, value)
        self.db.commit()
        self.db.refresh(user)
        cache.invalidate("users")
        cache.invalidate("dashboard")
        return UserRead.model_validate(user)

    def delete_user(self, user_id: str) -> dict:
        user = self.db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        user.is_active = False
        self.db.commit()
        cache.invalidate("users")
        cache.invalidate("dashboard")
        return {"message": "Usuário desativado com sucesso"}
