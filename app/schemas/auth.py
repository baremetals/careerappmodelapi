from typing import Any, List, Optional, Dict, Union

from pydantic import BaseModel, Field


class CreateUserRequest(BaseModel):
    email: str
    first_name: str
    last_name: str
    password: str
    company_name: str
    user_status: str
    user_role: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)
