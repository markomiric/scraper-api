from typing import Annotated

from annotated_types import MaxLen, MinLen
from pydantic import BaseModel, EmailStr


class UserSignUpRequest(BaseModel):
    email: EmailStr
    password: Annotated[str, MinLen(8)]

    class Config:
        schema_extra = {
            "example": {"email": "user@email.com", "password": "TestPassword123!"}
        }


class ConfirmUserRequest(BaseModel):
    email: EmailStr
    confirmation_code: Annotated[str, MaxLen(6)]

    class Config:
        schema_extra = {
            "example": {"email": "user@email.com", "confirmation_code": "123456"}
        }


class UserSignInRequest(BaseModel):
    email: EmailStr
    password: Annotated[str, MinLen(8)]

    class Config:
        schema_extra = {
            "example": {"email": "user@email.com", "password": "TestPassword123!"}
        }


class ConfirmForgotPasswordRequest(BaseModel):
    email: EmailStr
    confirmation_code: Annotated[str, MaxLen(6)]
    new_password: Annotated[str, MinLen(8)]

    class Config:
        schema_extra = {
            "example": {
                "email": "user@email.com",
                "confirmation_code": "123456",
                "new_password": "TestPassword123!",
            }
        }


class ChangePasswordRequest(BaseModel):
    old_password: Annotated[str, MinLen(8)]
    new_password: Annotated[str, MinLen(8)]
    access_token: str

    class Config:
        schema_extra = {
            "example": {
                "old_password": "OldPassword123!",
                "new_password": "NewPassword123!",
                "access_token": "Bearer token",
            }
        }


class RefreshTokenRequest(BaseModel):
    refresh_token: str

    class Config:
        schema_extra = {
            "example": {
                "refresh_token": "Bearer token",
            }
        }


class AccessTokenRequest(BaseModel):
    access_token: str

    class Config:
        schema_extra = {
            "example": {
                "access_token": "Bearer token",
            }
        }


class MessageResponse(BaseModel):
    message: str

    class Config:
        schema_extra = {
            "example": {
                "message": "Account confirmed successfully",
            }
        }


class UserResponse(BaseModel):
    id: str

    class Config:
        schema_extra = {
            "example": {
                "id": "1234567890",
            }
        }


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    id_token: str
    token_type: str
    expires_in: int

    class Config:
        schema_extra = {
            "example": {
                "access_token": "Bearer token",
                "refresh_token": "Bearer token",
                "id_token": "Bearer token",
                "token_type": "Bearer",
                "expires_in": 3600,
            }
        }
