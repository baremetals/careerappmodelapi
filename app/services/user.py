from datetime import datetime
from fastapi import HTTPException
from starlette import status
from app.config.guards import hash_password, verify_password, generate_api_key
from app.models.user import User, APIKey
from app.services.email import send_password_changed_confirmation_email
# from sqlalchemy import and_


async def fetch_user_detail(user_id, db):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        return user
    raise HTTPException(status_code=400, detail="User does not exists.")


async def change_user_password(user, db, user_verification, background_tasks):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Authentication Failed')

    user_model = db.get(User, user.get('user_id'))
    if not verify_password(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Incorrect details provided')
    if not user.verified_at:
        raise HTTPException(status_code=400, detail="Invalid request")

    if not user.user_status != 'active':
        raise HTTPException(status_code=400, detail="Invalid request")
    user_model.password = hash_password(user_verification.new_password)
    user.updated_at = datetime.now()
    db.add(user_model)
    db.commit()
    db.refresh(user_model)

    await send_password_changed_confirmation_email(user, background_tasks)
    return


async def create_user_api_key(user, db):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Authentication Failed')
    new_api_key = await generate_api_key()

    create_api_key_model = APIKey(
        key=new_api_key,
        user_id=user.get('user_id')
    )
    db.add(create_api_key_model)
    db.commit()
    db.refresh(create_api_key_model)
    return {"api_key": new_api_key}


async def revoke_user_api_key(key_id, user, db):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Authentication Failed')
    key_model = db.get(APIKey, key_id)
    if key_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Key not found')
    key_model.updated_at = datetime.now()
    db.add(key_model)
    db.commit()
    db.refresh(key_model)
    return


async def fetch_active_api_keys(user, db):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Authentication Failed')
    keys = db.query(APIKey).filter(APIKey.user_id == user.user_id, APIKey.isActive)
    # keys = db.query(APIKey).filter(and_(APIKey.user_id == user.user_id, APIKey.isActive))
    return {"api_keys": keys}
