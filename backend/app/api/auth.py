from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging

from ..api.dependencies import get_db, get_current_user, get_token
from ..core.security import create_access_token, decode_jwt_token
from ..models import User
from ..schemas.client import ClientBasicRead
from ..schemas.user import UserRead
from ..services.auth_service import AuthService
from ..core.config import settings

logger = logging.getLogger("auth")

router = APIRouter()

class LoginRequest(BaseModel):
    username: str | None = None
    password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@router.post("/login")
async def login(
    request: Request,
    db: Session = Depends(get_db),
    response: Response = None
):
    auth = AuthService(db)
    username = None
    password = None
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
    elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
    else:
        raise HTTPException(status_code=400, detail="Dados de login não fornecidos")
    if not username or not password:
        raise HTTPException(status_code=400, detail="username e password são obrigatórios")
    user = None
    # Usuário: username pode ser e-mail ou username
    if "@" in username:
        user = auth.authenticate_user_by_email(username, password)
    else:
        user = auth.authenticate_user_by_username(username, password)
    if user:
        token = create_access_token(
            subject=str(user.id),
            additional_claims={"role": user.role, "name": user.name}
        )
        logger.info(f"Login bem-sucedido para usuário {user.id}. Token gerado: {token}")
        if response:
            response.set_cookie(
                key="access_token",
                value=token,
                httponly=True,
                secure=False,
                samesite="lax",
                max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                path="/"
            )
            logger.info(f"Cookie 'access_token' setado para usuário {user.id}")
        return {"access_token": token, "token_type": "bearer", "user": UserRead.model_validate(user, from_attributes=True)}
    client = None
    if "@" in username:
        client = auth.authenticate_client_by_email(username, password)
    else:
        doc = ''.join(filter(str.isdigit, username))
        client = auth.authenticate_client(doc, password)
    if client:
        token = create_access_token(subject=str(client.id))
        logger.info(f"Login bem-sucedido para cliente {client.id}. Token gerado: {token}")
        if response:
            response.set_cookie(
                key="access_token",
                value=token,
                httponly=True,
                secure=False,
                samesite="lax",
                max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                path="/"
            )
            logger.info(f"Cookie 'access_token' setado para cliente {client.id}")
        return {"access_token": token, "token_type": "bearer", "client": ClientBasicRead.model_validate(client, from_attributes=True)}
    raise HTTPException(status_code=401, detail="Credenciais inválidas")


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token", path="/")
    return {"msg": "Logout realizado com sucesso"}


@router.patch("/change-password")
def change_password(password_data: ChangePasswordRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    auth = AuthService(db)
    if not auth.change_password(user, password_data.current_password, password_data.new_password):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")
    return {"msg": "Senha alterada com sucesso"}

@router.get("/check-token")
def check_token(token: str = Depends(get_token)):
    return decode_jwt_token(token)
