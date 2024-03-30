from app.config.guards import hash_password, validate_password_strength, verify_password, load_user, str_encode, \
    generate_token, str_decode, get_token_payload
from app.config.settings import get_settings
from app.models.user import User, UserToken
from fastapi import HTTPException
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload
from app.services.email import send_account_confirmation_email, send_password_reset_email, \
    send_password_changed_confirmation_email, send_account_activation_email
from app.utils.constants import USER_VERIFY_ACCOUNT, FORGOT_PASSWORD
from app.utils.utility_func import unique_string
from loguru import logger

settings = get_settings()


async def create_new_user(data, db, background_tasks):
    user_exist = db.query(User).filter(User.email == data.email).first()
    if user_exist:
        raise HTTPException(status_code=400, detail="Email already exists.")

    validate_password = validate_password_strength(data.password)
    if not validate_password:
        raise HTTPException(status_code=400, detail=validate_password)

    create_user_model = User(
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name,
        password=hash_password(data.password),
        company_name=data.company_name,
        user_status='active',
        updated_at=datetime.utcnow()
    )
    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)

    await send_account_activation_email(create_user_model, background_tasks)
    return create_user_model


async def verify_user_account(data, db, background_tasks):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="This link is not valid.")

    user_token = user.get_context_string(context=USER_VERIFY_ACCOUNT)
    try:
        token_valid = verify_password(user_token, data.token)
    except Exception as verify_exec:
        # logging.exception(verify_exec)
        logger.exception(verify_exec)
        token_valid = False
    if not token_valid:
        raise HTTPException(status_code=400, detail="This link either expired or not valid.")

    user.user_status = True
    user.updated_at = datetime.utcnow()
    user.verified_at = datetime.utcnow()
    db.add(user)
    db.commit()
    db.refresh(user)

    await send_account_confirmation_email(user, background_tasks)
    return user


async def get_login_token(data, db):
    user = await load_user(data.username, db)
    if not user or verify_password(data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect email or password.")

    if not user.verified_at:
        raise HTTPException(status_code=400,
                            detail="Your account is not verified. Please check your email "
                                   "inbox to verify your account.")

    if not user.user_status != 'active':
        raise HTTPException(status_code=400, detail="Your account has been dactivated. Please contact support.")

    # Generate the JWT Token
    return _generate_tokens(user, db)


async def get_refresh_token(refresh_token, session):
    token_payload = get_token_payload(refresh_token, settings.SECRET_KEY, settings.JWT_ALGORITHM)
    if not token_payload:
        raise HTTPException(status_code=400, detail="Invalid Request.")

    refresh_key = token_payload.get('t')
    access_key = token_payload.get('a')
    user_id = str_decode(token_payload.get('sub'))
    user_token = session.query(UserToken).options(joinedload(UserToken.user)).filter(
        UserToken.refresh_key == refresh_key,
        UserToken.access_key == access_key,
        UserToken.user_id == user_id,
        UserToken.expires_at > datetime.utcnow()
    ).first()
    if not user_token:
        raise HTTPException(status_code=400, detail="Invalid Request.")

    user_token.expires_at = datetime.utcnow()
    session.add(user_token)
    session.commit()
    return _generate_tokens(user_token.user, session)


def _generate_tokens(user, session):
    refresh_key = unique_string(100)
    access_key = unique_string(50)
    rt_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    user_token = UserToken()
    user_token.user_id = user.id
    user_token.refresh_key = refresh_key
    user_token.access_key = access_key
    user_token.expires_at = datetime.utcnow() + rt_expires
    session.add(user_token)
    session.commit()
    session.refresh(user_token)

    at_payload = {
        "sub": str_encode(str(user.id)),
        'a': access_key,
        'r': str_encode(str(user_token.id)),
        'n': str_encode(f"{user.name}")
    }

    at_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = generate_token(at_payload, settings.JWT_SECRET, settings.JWT_ALGORITHM, at_expires)

    rt_payload = {"sub": str_encode(str(user.id)), "t": refresh_key, 'a': access_key}
    refresh_token = generate_token(rt_payload, settings.SECRET_KEY, settings.JWT_ALGORITHM, rt_expires)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": at_expires.seconds
    }


async def send_forgot_password_link(data, background_tasks, db):
    user = await load_user(data.email, db)
    if not user.verified_at:
        raise HTTPException(status_code=400,
                            detail="Your account is not verified. Please check your email inbox to "
                                   "verify your account.")

    if not user.user_status != 'active':
        raise HTTPException(status_code=400, detail="Your account has been dactivated. Please contact support.")

    await send_password_reset_email(user, background_tasks)


async def reset_user_password(data, db, background_tasks):
    user = await load_user(data.email, db)

    if not user:
        raise HTTPException(status_code=400, detail="Invalid request")

    if not user.verified_at:
        raise HTTPException(status_code=400, detail="Invalid request")

    if not user.user_status != 'active':
        raise HTTPException(status_code=400, detail="Invalid request")

    user_token = user.get_context_string(context=FORGOT_PASSWORD)
    try:
        token_valid = verify_password(user_token, data.token)
    except Exception as verify_exec:
        logger.exception(verify_exec)
        token_valid = False
    if not token_valid:
        raise HTTPException(status_code=400, detail="Invalid window.")

    user.password = hash_password(data.password)
    user.updated_at = datetime.now()
    db.add(user)
    db.commit()
    db.refresh(user)

    await send_password_changed_confirmation_email(user, background_tasks)
