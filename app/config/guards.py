from typing import Union, Annotated

from loguru import logger
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, Request
from jose import jwt
import base64
import secrets

from sqlalchemy.orm import joinedload
from starlette import status

from app.config.database import get_db
from app.config.settings import get_settings
from app.models.user import UserToken, APIKey

settings = get_settings()

db_dependency = Annotated[Session, Depends(get_db)]

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')
SPECIAL_CHARACTERS = ['@', '#', '$', '%', '=', ':', '?', '.', '/', '|', '~', '>']
special_char_str = ", ".join(SPECIAL_CHARACTERS)


def str_encode(string: str) -> str:
    return base64.b85encode(string.encode('ascii')).decode('ascii')


def str_decode(string: str) -> str:
    return base64.b85decode(string.encode('ascii')).decode('ascii')


def get_token_payload(token: str, secret: str, algo: str):
    try:
        payload = jwt.decode(token, secret, algorithms=algo)
    except Exception as jwt_exec:
        logger.exception(jwt_exec)
        # logging.debug(f"JWT Error: {str(jwt_exec)}")
        payload = None
    return payload


def hash_password(password):
    return bcrypt_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)


def validate_password_strength(password: str) -> Union[str, bool]:
    if len(password) < 8:
        return 'Password must be at least 8 characters'
    if not any(char.isdigit() for char in password):
        return 'Password must contain at least one digit'
    if not any(char.isupper() for char in password):
        return 'Password must contain at least one uppercase letter'
    if not any(char.islower() for char in password):
        return 'Password must contain at least one lowercase letter'
    if not any(char in SPECIAL_CHARACTERS for char in password):
        return f"Password must contain at least one special character, {special_char_str}"
    return True


async def load_user(email: str, db):
    from app.models.user import User
    try:
        user = db.query(User).filter(User.email == email).first()
    except Exception as user_exec:
        logger.exception(user_exec)
        logger.info(f"User Not Found, Email: {email}")
        user = None
    return user


def generate_token(payload: dict, secret: str, algo: str, expiry: timedelta):
    expire = datetime.utcnow() + expiry
    payload.update({"exp": expire})
    return jwt.encode(payload, secret, algorithm=algo)


async def get_current_user(db: db_dependency, token: str = Depends(oauth2_bearer)):
    user = await get_token_user(token=token, db=db)
    if user:
        return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail='Authentication Failed')


async def get_token_user(token: str, db):
    payload = get_token_payload(token, settings.JWT_SECRET, settings.JWT_ALGORITHM)
    if payload:
        user_token_id = str_decode(payload.get('r'))
        user_id = str_decode(payload.get('sub'))
        access_key = payload.get('a')
        user_token = db.query(UserToken).options(joinedload(UserToken.user)).filter(UserToken.access_key == access_key,
                                                                                    UserToken.id == user_token_id,
                                                                                    UserToken.user_id == user_id,
                                                                                    UserToken.expires_at >
                                                                                    datetime.utcnow()).first()
        if user_token:
            return user_token.user
    return None


async def generate_api_key():
    return secrets.token_urlsafe(32)


async def verify_api_key(request: Request, db: db_dependency):
    api_key = request.headers.get("Authorization")
    if not api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key is required")

    api_key_obj = db.query(APIKey).filter(APIKey.key == api_key).first()
    if not api_key_obj or not api_key_obj.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or inactive API key")

    return api_key_obj
