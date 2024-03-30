from typing import Annotated
from fastapi import APIRouter, Depends, BackgroundTasks, Header
from sqlalchemy.orm import Session
from starlette import status
from fastapi.responses import JSONResponse
from app.config.database import get_db
from app.config.guards import oauth2_bearer, get_current_user
from app.responses.user_responses import UserResponse, LoginResponse
from app.schemas.auth import CreateUserRequest, Token, UserVerificationRequest, EmailRequest, ResetRequest
from fastapi.security import OAuth2PasswordRequestForm
from app.services import auth

router = APIRouter(
    prefix='/auth',
    tags=['auth'],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(oauth2_bearer), Depends(get_current_user)]
)


db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register_user(data: CreateUserRequest, background_tasks: BackgroundTasks, db: db_dependency):
    return await auth.create_new_user(data, db, background_tasks)


@router.post("/verify", status_code=status.HTTP_200_OK)
async def verify_user_account(data: UserVerificationRequest, background_tasks: BackgroundTasks,
                              db: db_dependency):
    await auth.verify_user_account(data, db, background_tasks)
    return JSONResponse({"message": "Account is activated successfully."})


@router.post("/login", response_model=LoginResponse)
async def login_user(data: Annotated[OAuth2PasswordRequestForm, Depends()],
                     db: db_dependency):
    return await auth.get_login_token(data, db)


@router.post("/refresh", status_code=status.HTTP_200_OK, response_model=LoginResponse)
async def refresh_token(db: db_dependency, token=Header()):
    return await auth.get_refresh_token(token, db)


@router.post("/forgot-password", response_model=Token)
async def forgot_password(data: EmailRequest, background_tasks: BackgroundTasks,
                          db: db_dependency):
    await auth.send_forgot_password_link(data, background_tasks, db)
    return JSONResponse({"message": "A email with password reset link has been sent to you."})


@router.post("/reset-password", response_model=Token)
async def reset_password(data: ResetRequest, background_tasks: BackgroundTasks, db: db_dependency):
    await auth.reset_user_password(data, db, background_tasks)
    return JSONResponse({"message": "Your password has been updated."})
