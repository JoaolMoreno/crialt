from datetime import datetime, timedelta, UTC
from typing import Any, Union

from jose import jwt
from passlib.context import CryptContext

from ..core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = settings.ALGORITHM


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None, additional_claims: dict = None
) -> str:
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    if additional_claims:
        to_encode.update(additional_claims)
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def decode_jwt_token(token: str) -> dict:
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        if decoded_token["exp"] >= datetime.now(UTC).timestamp():
            return decoded_token
        else:
            return {}
    except jwt.JWTError:
        return {}
