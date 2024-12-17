import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, status

from src.common.schema import MessageResponse
from src.dependencies import get_current_user, has_roles
from src.user.schema import UserProfileResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["User"])  # Changed tags to a list


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
