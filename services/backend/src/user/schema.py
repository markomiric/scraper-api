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


class MessageResponse(BaseSchema):
    message: str = Field(..., description="Response message")


class AuthResponse(BaseSchema):
    AccessToken: str = Field(..., description="JWT access token")
    RefreshToken: str = Field(..., description="JWT refresh token")
    IdToken: str = Field(..., description="JWT ID token")
    TokenType: str = Field(..., description="Token type (Bearer)")
    ExpiresIn: int = Field(..., description="Token expiration in seconds")


class UserProfileResponse(BaseSchema):
    sub: str = Field(..., description="Unique identifier for the user")
    email: EmailStr = Field(..., description="User's email address")
    email_verified: bool = Field(..., description="Email verification status")
    username: str = Field(..., description="User's username")
    groups: list[str] = Field(
        ..., alias="cognito:groups", description="User's group memberships"
    )
    issuer: str = Field(..., alias="iss", description="Token issuer URL")
    client_id: str = Field(..., description="OAuth 2.0 client identifier")
    origin_jti: str = Field(..., description="Original JWT ID")
    event_id: str = Field(..., description="Event identifier")
    token_use: str = Field(..., description="Token usage type")
    scope: str = Field(..., description="OAuth 2.0 scope")
    auth_time: int = Field(..., description="Authentication timestamp")
    exp: int = Field(..., description="Token expiration timestamp")
    iat: int = Field(..., description="Token issuance timestamp")
    jti: str = Field(..., description="JWT ID")
