from fastapi import BackgroundTasks

from app.config.sendgrid_email import send_email
from app.config.settings import get_settings
from app.models.user import User
from app.utils.constants import USER_VERIFY_ACCOUNT, FORGOT_PASSWORD

settings = get_settings()


async def send_account_activation_email(user: User, background_task: BackgroundTasks):
    from app.config.guards import hash_password
    string_context = user.get_context_string(context=USER_VERIFY_ACCOUNT)
    token = hash_password(string_context)
    activate_url = f"{settings.FRONTEND_HOST}/auth/account-verify?token={token}&email={user.email}"
    data = {
        'app_name': settings.PROJECT_NAME,
        "name": user.frist_name,
        'activate_url': activate_url
    }
    subject = f"Account Verification - {settings.APP_NAME}"
    await send_email(
        recipient=user.email,
        subject=subject,
        content=data,
        background_tasks=background_task
    )


async def send_account_confirmation_email(user: User, background_tasks: BackgroundTasks):
    data = {
        'app_name': settings.PROJECT_NAME,
        "name": user.first_name,
        'login_url': f'{settings.FRONTEND_HOST}'
    }
    subject = f"Welcome - {settings.PROJECT_NAME}"
    await send_email(
        recipient=user.email,
        subject=subject,
        content=data,
        background_tasks=background_tasks
    )


async def send_password_reset_email(user: User, background_tasks: BackgroundTasks):
    from app.config.guards import hash_password
    string_context = user.get_context_string(context=FORGOT_PASSWORD)
    token = hash_password(string_context)
    reset_url = f"{settings.FRONTEND_HOST}/reset-password?token={token}&email={user.email}"
    data = {
        'app_name': settings.PROJECT_NAME,
        "name": user.first_name,
        'activate_url': reset_url,
    }
    subject = f"Reset Password - {settings.PROJECT_NAME}"
    await send_email(
        recipient=user.email,
        subject=subject,
        content=data,
        background_tasks=background_tasks
    )


async def send_password_changed_confirmation_email(user: User, background_tasks: BackgroundTasks):
    from app.config.guards import hash_password
    string_context = user.get_context_string(context=FORGOT_PASSWORD)
    token = hash_password(string_context)
    reset_url = f"{settings.FRONTEND_HOST}/reset-password?token={token}&email={user.email}"
    data = {
        'app_name': settings.PROJECT_NAME,
        "name": user.first_name,
        'activate_url': reset_url,
    }
    subject = f"Reset Password - {settings.PROJECT_NAME}"
    await send_email(
        recipient=user.email,
        subject=subject,
        content=data,
        background_tasks=background_tasks
    )
