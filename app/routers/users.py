from typing import Annotated
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from starlette import status
from app.config.database import get_db
from app.config.guards import get_current_user
from app.responses.user_responses import UserResponse, CreateAPKeyResponse, FetchAPKeysResponse
from app.schemas.auth import ChangePasswordRequest
from passlib.context import CryptContext
from app.services import user as user_service

router = APIRouter(
    prefix='/user',
    tags=['user'],
    responses={404: {"description": "Not found"}},
)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency):
    return user


@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user_info(user_id, db: db_dependency):
    return await user_service.fetch_user_detail(user_id, db)


@router.put("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password_request(user: user_dependency, db: db_dependency,
                                  user_verification: ChangePasswordRequest, background_tasks: BackgroundTasks):
    return await user_service.change_user_password(user, db, user_verification, background_tasks)


@router.get("/generate-api-key", status_code=status.HTTP_201_CREATED,
            response_model=CreateAPKeyResponse)
async def create_api_key(user: user_dependency, db: db_dependency):
    return await user_service.create_user_api_key(user, db)


@router.get("/revoke-api-key/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(key_id, user: user_dependency, db: db_dependency):
    return await user_service.revoke_user_api_key(key_id, user, db)


@router.get("/api-keys", status_code=status.HTTP_201_CREATED, response_model=FetchAPKeysResponse)
async def fetch_api_key(user: user_dependency, db: db_dependency):
    return await user_service.fetch_active_api_keys(user, db)
