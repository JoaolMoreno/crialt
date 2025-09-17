import logging

from starlette.status import HTTP_403_FORBIDDEN

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security.utils import get_authorization_scheme_param

from ..core.security import decode_jwt_token
from ..models.user import User
from ..models.client import Client
from ..core.database import SessionLocal
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from fastapi import Request

class OAuth2PasswordBearerWithCookie(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> str | None:
        auth_header = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(auth_header)
        if scheme and scheme.lower() == "bearer" and param:
            return param
        token = request.cookies.get("access_token")
        if token:
            return token
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
        )

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/api/v1/auth/login")


def get_db() -> Generator:
    logger.debug('Entrando em get_db')
    db = None
    try:
        db = SessionLocal()
        logger.debug('Sessão DB criada')
        yield db
    finally:
        if db:
            logger.debug('Fechando sessão DB')
            db.close()


async def get_token(request: Request) -> str | None:
    auth_header = request.headers.get("Authorization")
    scheme, param = get_authorization_scheme_param(auth_header)
    token = None
    if scheme.lower() == "bearer" and param:
        token = param
        logger.debug(f"Token lido do header Authorization: {token}")
    else:
        token = request.cookies.get("access_token")
        logger.debug(f"Token lido do cookie: {token}")
    if not token:
        logger.warning("Nenhum token encontrado no header ou cookie")
    return token


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    logger.debug(f'Entrando em get_current_user com token={token}')
    if not token:
        logger.warning('Token ausente na requisição')
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token ausente")
    try:
        payload = decode_jwt_token(token)
        logger.debug(f'Payload decodificado: {payload}')
        if not payload or not isinstance(payload, dict):
            logger.debug('Payload inválido ou vazio')
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
        user_id = payload.get("sub")
        if user_id is None:
            logger.debug('user_id não encontrado no payload')
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
        user = db.query(User).filter(User.id == user_id).first()
        logger.debug(f'Usuário encontrado: {user}')
        if user is None or not user.is_active:
            logger.debug('Usuário não encontrado ou inativo')
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado ou inativo")
        logger.debug('Usuário autenticado com sucesso')
        return user
    except Exception as e:
        logger.debug(f'Exceção em get_current_user: {e}')
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")


def get_current_actor(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db), allowed_roles: list = None):
    logger.debug(f'Entrando em get_current_actor com token={token}, allowed_roles={allowed_roles}')
    try:
        if not token:
            logger.warning('Token ausente na requisição')
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token ausente")
        payload = decode_jwt_token(token)
        logger.debug(f'Payload decodificado: {payload}')
        actor_id = payload.get("sub")
        if actor_id is None:
            logger.debug('actor_id não encontrado no payload')
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
        user = db.query(User).filter(User.id == actor_id).first()
        logger.debug(f'Usuário encontrado: {user}')
        if user and user.is_active:
            if allowed_roles and getattr(user, "role", None) not in allowed_roles:
                logger.debug(f'Usuário não tem role permitida: {user.role}')
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
            logger.debug('Usuário ativo retornado')
            return user
        client = db.query(Client).filter(Client.id == actor_id).first()
        logger.debug(f'Cliente encontrado: {client}')
        if client and client.is_active:
            if allowed_roles and "client" not in allowed_roles:
                logger.debug('Cliente não tem role permitida')
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
            logger.debug('Cliente ativo retornado')
            return client
        logger.debug('Usuário ou cliente não encontrado ou inativo')
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário ou cliente não encontrado ou inativo")
    except Exception as e:
        logger.debug(f'Exceção em get_current_actor: {e}')
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")


def get_current_actor_factory(allowed_roles: list = None):
    def _get_current_actor(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        logger.debug(f'Entrando em get_current_actor com token={token}, allowed_roles={allowed_roles}')
        try:
            if not token:
                logger.warning('Token ausente na requisição')
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token ausente")
            payload = decode_jwt_token(token)
            logger.debug(f'Payload decodificado: {payload}')
            actor_id = payload.get("sub")
            if actor_id is None:
                logger.debug('actor_id não encontrado no payload')
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
            user = db.query(User).filter(User.id == actor_id).first()
            logger.debug(f'Usuário encontrado: {user}')
            if user and user.is_active:
                if allowed_roles and getattr(user, "role", None) not in allowed_roles:
                    logger.debug(f'Usuário não tem role permitida: {user.role}')
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
                logger.debug('Usuário ativo retornado')
                return user
            client = db.query(Client).filter(Client.id == actor_id).first()
            logger.debug(f'Cliente encontrado: {client}')
            if client and client.is_active:
                if allowed_roles and "client" not in allowed_roles:
                    logger.debug('Cliente não tem role permitida')
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
                logger.debug('Cliente ativo retornado')
                return client
            logger.debug('Usuário ou cliente não encontrado ou inativo')
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário ou cliente não encontrado ou inativo")
        except Exception as e:
            logger.debug(f'Exceção em get_current_actor: {e}')
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    return _get_current_actor


def client_resource_permission(resource_client_ids: list, actor = Depends(get_current_actor)):
    logger.debug(f'Entrando em client_resource_permission com resource_client_ids={resource_client_ids}, actor={actor}')
    # Se for usuário admin, libera
    if hasattr(actor, "role") and getattr(actor, "role", None) == "admin":
        logger.debug('Permissão concedida: usuário admin')
        return True
    # Se for cliente, libera se o id estiver na lista
    if hasattr(actor, "id") and str(actor.id) in resource_client_ids:
        logger.debug('Permissão concedida: cliente com id na lista')
        return True
    # Se for usuário comum, libera se o client_id estiver na lista
    if hasattr(actor, "client_id") and str(actor.client_id) in resource_client_ids:
        logger.debug('Permissão concedida: usuário comum com client_id na lista')
        return True
    logger.debug('Permissão negada ao recurso')
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado ao recurso")
