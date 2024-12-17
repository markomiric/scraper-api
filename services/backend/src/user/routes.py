import logging
from typing import Any, Dict

from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import EmailStr

from src.aws.cognito import Cognito
from src.dependencies import get_cognito, get_current_user, has_roles
from src.user.schema import (
    AuthResponse,
    ChangePasswordRequest,
    ConfirmForgotPasswordRequest,
    ConfirmUserRequest,
    MessageResponse,
    RefreshTokenRequest,
    UserIdResponse,
    UserProfileResponse,
    UserSignInRequest,
    UserSignUpRequest,
)

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer()

router = APIRouter(prefix="/auth", tags=["Authentication"])  # Changed tags to a list


def handle_cognito_error(e: ClientError) -> None:
    """Standardized Cognito error handling"""
    logger.error(f"Cognito error: {str(e)}")
    raise HTTPException(
        status_code=e.response["ResponseMetadata"]["HTTPStatusCode"],
        detail=e.response["Error"]["Message"],
    )


@router.post(
    "/sign_up", response_model=UserIdResponse, status_code=status.HTTP_201_CREATED
)
async def sign_up(
    user: UserSignUpRequest, cognito: Cognito = Depends(get_cognito)
) -> UserIdResponse:
    """Register a new user."""
    try:
        response = cognito.sign_up(user)
        logger.info(f"User registered: {user.email}")
        return UserIdResponse(sub=response["UserSub"])
    except ClientError as e:
        handle_cognito_error(e)


@router.post(
    "/sign_up/confirm", response_model=MessageResponse, status_code=status.HTTP_200_OK
)
async def confirm_sign_up(
    data: ConfirmUserRequest, cognito: Cognito = Depends(get_cognito)
) -> MessageResponse:
    """Confirm user registration."""
    try:
        cognito.confirm_sign_up(data)
        cognito.admin_add_user_to_group(username=data.email, group_name="User")
        logger.info(f"User confirmed: {data.email}")
        return MessageResponse(message="Account confirmed successfully")
    except ClientError as e:
        handle_cognito_error(e)


@router.post(
    "/confirmation_code/resend",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
async def resend_confirmation_code(
    email: EmailStr, cognito: Cognito = Depends(get_cognito)
) -> MessageResponse:
    """Resend confirmation code to user email."""
    try:
        cognito.resend_confirmation_code(email)
        logger.info(f"Confirmation code resent to: {email}")
        return MessageResponse(message="Confirmation code resent successfully")
    except ClientError as e:
        handle_cognito_error(e)


@router.post("/sign_in", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def sign_in(
    payload: UserSignInRequest, cognito: Cognito = Depends(get_cognito)
) -> AuthResponse:
    """Authenticate user and return tokens."""
    try:
        response = cognito.authenticate_user(payload)
        logger.info(f"User signed in: {payload.email}")
        return AuthResponse(**response["AuthenticationResult"])
    except ClientError as e:
        handle_cognito_error(e)


@router.post(
    "/forgot_password", response_model=MessageResponse, status_code=status.HTTP_200_OK
)
async def forgot_password(
    email: EmailStr, cognito: Cognito = Depends(get_cognito)
) -> MessageResponse:
    """Initiate password reset process."""
    try:
        cognito.forgot_password(email)
        logger.info(f"Password reset initiated for: {email}")
        return MessageResponse(message="Password reset code sent to your email address")
    except ClientError as e:
        handle_cognito_error(e)


@router.post(
    "/forgot_password/confirm",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
async def confirm_forgot_password(
    data: ConfirmForgotPasswordRequest, cognito: Cognito = Depends(get_cognito)
) -> MessageResponse:
    """Confirm password reset with code."""
    try:
        cognito.confirm_forgot_password(data)
        logger.info(f"Password reset confirmed for: {data.email}")
        return MessageResponse(message="Password reset successful")
    except ClientError as e:
        handle_cognito_error(e)


@router.post(
    "/change_password", response_model=MessageResponse, status_code=status.HTTP_200_OK
)
async def change_password(
    data: ChangePasswordRequest, cognito: Cognito = Depends(get_cognito)
) -> MessageResponse:
    """Change user's password."""
    try:
        cognito.change_password(data)
        logger.info(f"Password changed for user: {data.email}")
        return MessageResponse(message="Password changed successfully")
    except ClientError as e:
        handle_cognito_error(e)


@router.post("/token/refresh", status_code=status.HTTP_200_OK)
async def authenticate_refresh_token(
    payload: RefreshTokenRequest, cognito: Cognito = Depends(get_cognito)
):
    """Authenticate user with refresh token."""
    try:
        response = cognito.authenticate_refresh_token(payload.refresh_token)
    except ClientError as e:
        handle_cognito_error(e)
    return JSONResponse(content=response["AuthenticationResult"], status_code=200)


@router.post("/sign_out", status_code=status.HTTP_204_NO_CONTENT)
async def sign_out(
    token: HTTPAuthorizationCredentials = Security(bearer_scheme),
    cognito: Cognito = Depends(get_cognito),
) -> None:
    """Sign out user by revoking tokens."""
    try:
        cognito.sign_out(token.credentials)
        logger.info("User logged out")
    except ClientError as e:
        handle_cognito_error(e)


@router.get("/admin", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def admin_endpoint(_: Any = Depends(has_roles(["Admin"]))) -> MessageResponse:
    """Endpoint accessible only by admin users."""
    logger.info("Admin endpoint accessed")
    return MessageResponse(message="Welcome, admin user")


@router.get("/me", response_model=UserProfileResponse, status_code=status.HTTP_200_OK)
async def me(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> UserProfileResponse:
    """Retrieve current user's information."""
    logger.info(f"User profile accessed: {current_user.get('email')}")
    return UserProfileResponse(**current_user)
