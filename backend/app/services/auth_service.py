from typing import Optional
from sqlalchemy.orm import Session

from app.core.security import verify_password, get_password_hash
from app.models import User, Client
from app.schemas.user import UserRole


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.db.query(User).filter(User.email == email).first()
        if user and verify_password(password, user.password_hash):
            return user
        return None

    def authenticate_client(self, email: str, password: str) -> Optional[Client]:
        client = self.db.query(Client).filter(Client.email == email).first()
        if client and verify_password(password, client.password_hash):
            return client
        return None

    def authenticate_user_by_username(self, username: str, password: str) -> Optional[User]:
        user = self.db.query(User).filter(User.username == username).first()
        if user and verify_password(password, user.password_hash):
            return user
        return None

    def authenticate_user_by_email(self, email: str, password: str) -> Optional[User]:
        user = self.db.query(User).filter(User.email == email).first()
        if user and verify_password(password, user.password_hash):
            return user
        return None

    def check_role(self, user: User, role: UserRole) -> bool:
        return user.role == role

    def change_password(self, user: User, current_password: str, new_password: str) -> bool:
        if not verify_password(current_password, user.password_hash):
            return False
        user.password_hash = get_password_hash(new_password)
        self.db.commit()
        return True

    def reset_client_password(self, client: Client, new_password: Optional[str] = None) -> str:
        if not new_password:
            new_password = "crialt" + str(client.id)[-4:]  # simples, pode ser melhorado
        client.password_hash = get_password_hash(new_password)
        client.first_access = True
        self.db.commit()
        return new_password
