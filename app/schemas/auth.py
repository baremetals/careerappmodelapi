from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class CreateUserRequest(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    company_name: str
    user_status: Optional[str] = 'active'
    user_role: Optional[str] = 'user'


class Token(BaseModel):
    access_token: str
    token_type: str


class ChangePasswordRequest(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


class UserVerificationRequest(BaseModel):
    token: str
    email: EmailStr


class EmailRequest(BaseModel):
    email: EmailStr


class ResetRequest(BaseModel):
    token: str
    email: EmailStr
    password: str
