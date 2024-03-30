from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.config.database import get_db
from app.config.guards import get_current_user
from app.models.user import User

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/users", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Authentication Failed')
    return db.query(User).all()

