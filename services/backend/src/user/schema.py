from pydantic import EmailStr, Field

from src.common.schema import BaseSchema


class UserProfileResponse(BaseSchema):
    sub: str = Field(..., description="Unique identifier for the user")
    email: EmailStr = Field(..., description="User's email address")
    email_verified: bool = Field(..., description="Email verification status")
    # username: str = Field(..., description="User's username")
    roles: list[str] = Field(..., description="User's group memberships")
    # issuer: str = Field(..., alias="iss", description="Token issuer URL")
    # client_id: str = Field(..., description="OAuth 2.0 client identifier")
    # origin_jti: str = Field(..., description="Original JWT ID")
    # event_id: str = Field(..., description="Event identifier")
    # token_use: str = Field(..., description="Token usage type")
    # scope: str = Field(..., description="OAuth 2.0 scope")
    # auth_time: int = Field(..., description="Authentication timestamp")
    # exp: int = Field(..., description="Token expiration timestamp")
    # iat: int = Field(..., description="Token issuance timestamp")
    # jti: str = Field(..., description="JWT ID")
