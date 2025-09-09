from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.dependencies import get_db, get_current_user
from app.core.security import create_access_token
from app.models import User
from app.schemas.client import ClientRead
from app.schemas.user import UserRead
from app.services.auth_service import AuthService

router = APIRouter()

class LoginRequest(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@router.post("/login")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    auth = AuthService(db)
    user = None
    if login_data.username:
        user = auth.authenticate_user_by_username(login_data.username, login_data.password)
    if not user and login_data.email:
        user = auth.authenticate_user_by_email(login_data.email, login_data.password)
    if user:
        token = create_access_token(subject=str(user.id))
        return {"access_token": token, "user": UserRead.model_validate(user, from_attributes=True)}
    client = None
    if login_data.email:
        client = auth.authenticate_client(login_data.email, login_data.password)
    if client:
        token = create_access_token(subject=str(client.id))
        return {"access_token": token, "client": ClientRead.model_validate(client, from_attributes=True)}
    raise HTTPException(status_code=401, detail="Credenciais inválidas")

@router.patch("/change-password")
def change_password(password_data: ChangePasswordRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    auth = AuthService(db)
    if not auth.change_password(user, password_data.current_password, password_data.new_password):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")
    return {"msg": "Senha alterada com sucesso"}
