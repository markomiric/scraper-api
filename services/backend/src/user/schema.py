from typing import Annotated

from annotated_types import MaxLen, MinLen
from pydantic import BaseModel, EmailStr


class UserSignUpRequest(BaseModel):
    email: EmailStr
    password: Annotated[str, MinLen(8)]


class ConfirmUserRequest(BaseModel):
    email: EmailStr
    confirmation_code: Annotated[str, MaxLen(6)]


class UserSignInRequest(BaseModel):
    email: EmailStr
    password: Annotated[str, MinLen(8)]


class ConfirmForgotPasswordRequest(BaseModel):
    email: EmailStr
    confirmation_code: Annotated[str, MaxLen(6)]
    new_password: Annotated[str, MinLen(8)]


class ChangePasswordRequest(BaseModel):
    old_password: Annotated[str, MinLen(8)]
    new_password: Annotated[str, MinLen(8)]
    access_token: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class AccessTokenRequest(BaseModel):
    access_token: str


class MessageResponse(BaseModel):
    message: str


class UserResponse(BaseModel):
    id: str


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    id_token: str
    token_type: str
    expires_in: int
