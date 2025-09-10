from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm

from ..api.dependencies import get_db, get_current_user
from ..core.security import create_access_token
from ..models import User
from ..schemas.client import ClientRead
from ..schemas.user import UserRead
from ..services.auth_service import AuthService
from ..core.config import settings

router = APIRouter()

class LoginRequest(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@router.post("/login")
def login(
    login_data: LoginRequest = None,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    response: Response = None
):
    auth = AuthService(db)
    # Prioriza dados do formulário se presentes
    username = form_data.username if form_data and form_data.username else (login_data.username if login_data else None)
    email = None
    password = form_data.password if form_data and form_data.password else (login_data.password if login_data else None)
    # Se username for email, trata como email
    if username and "@" in username:
        email = username
        username = None
    elif login_data and login_data.email:
        email = login_data.email
    user = None
    if username:
        user = auth.authenticate_user_by_username(username, password)
    if not user and email:
        user = auth.authenticate_user_by_email(email, password)
    if user:
        token = create_access_token(subject=str(user.id))
        if response:
            response.set_cookie(
                key="access_token",
                value=token,
                httponly=True,
                secure= False,
                samesite="lax",
                max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                path="/"
            )
        return {"access_token": token, "token_type": "bearer", "user": UserRead.model_validate(user, from_attributes=True)}
    client = None
    if email:
        client = auth.authenticate_client(email, password)
    if client:
        token = create_access_token(subject=str(client.id))
        if response:
            response.set_cookie(
                key="access_token",
                value=token,
                httponly=True,
                secure=True, # Em produção, use True. Para dev, pode ser False.
                samesite="lax",
                max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                path="/"
            )
        return {"access_token": token, "token_type": "bearer", "client": ClientRead.model_validate(client, from_attributes=True)}
    raise HTTPException(status_code=401, detail="Credenciais inválidas")

@router.patch("/change-password")
def change_password(password_data: ChangePasswordRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    auth = AuthService(db)
    if not auth.change_password(user, password_data.current_password, password_data.new_password):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")
    return {"msg": "Senha alterada com sucesso"}
