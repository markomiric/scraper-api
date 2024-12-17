from typing import Annotated

from annotated_types import MaxLen, MinLen
from pydantic import EmailStr, Field

from src.common.schema import BaseSchema


class UserSignUpRequest(BaseSchema):
    email: EmailStr = Field(..., description="User's email address")
    password: Annotated[str, MinLen(8)] = Field(..., description="User's password")


class ConfirmUserRequest(BaseSchema):
    email: EmailStr = Field(..., description="User's email address")
    confirmation_code: Annotated[str, MaxLen(6)] = Field(
        ..., description="6-digit confirmation code"
    )


class UserSignInRequest(BaseSchema):
    email: EmailStr = Field(..., description="User's email address")
    password: Annotated[str, MinLen(8)] = Field(..., description="User's password")


class ConfirmForgotPasswordRequest(BaseSchema):
    email: EmailStr = Field(..., description="User's email address")
    confirmation_code: Annotated[str, MaxLen(6)] = Field(
        ..., description="6-digit confirmation code"
    )
    new_password: Annotated[str, MinLen(8)] = Field(..., description="New password")


class ChangePasswordRequest(BaseSchema):
    old_password: Annotated[str, MinLen(8)] = Field(..., description="Current password")
    new_password: Annotated[str, MinLen(8)] = Field(..., description="New password")
    access_token: str = Field(..., description="Valid access token")


class RefreshTokenRequest(BaseSchema):
    refresh_token: str = Field(..., description="Valid refresh token")


class UserIdResponse(BaseSchema):
    sub: str = Field(..., description="User ID")


class AuthResponse(BaseSchema):
    AccessToken: str = Field(..., description="JWT access token")
    RefreshToken: str = Field(..., description="JWT refresh token")
    IdToken: str = Field(..., description="JWT ID token")
    TokenType: str = Field(..., description="Token type (Bearer)")
    ExpiresIn: int = Field(..., description="Token expiration in seconds")
