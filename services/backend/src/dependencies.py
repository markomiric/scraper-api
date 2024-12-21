import os
from typing import Any, Dict

import httpx
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwk, jwt

from src.aws.cognito import Cognito
from src.config import get_settings
from src.job.store import JobStore

settings = get_settings()


def get_job_store() -> JobStore:
    return JobStore(settings.TABLE_NAME, dynamodb_url=settings.DYNAMODB_URL)


def get_cognito() -> Cognito:
    return Cognito(
        region_name=settings.AWS_REGION,
        user_pool_id=settings.AWS_USER_POOL_ID,
        user_pool_client_id=settings.AWS_USER_POOL_CLIENT_ID,
    )


bearer_scheme = HTTPBearer()

_httpx_client: httpx.AsyncClient = None
_jwks_cache: Dict[str, Any] = None


async def get_jwks():
    global _httpx_client, _jwks_cache

    if _jwks_cache is None:
        if _httpx_client is None:
            _httpx_client = httpx.AsyncClient()

        jwks_url = f"https://cognito-idp.{settings.AWS_REGION}.amazonaws.com/{settings.AWS_USER_POOL_ID}/.well-known/jwks.json"
        response = await _httpx_client.get(jwks_url)
        _jwks_cache = response.json()

    if not _jwks_cache.get("keys"):
        raise HTTPException(status_code=401, detail="No JWKS keys found")

    return _jwks_cache


def _convert_attribute_value(name: str, value: str) -> Any:
    """Convert Cognito attribute values to appropriate Python types."""
    if name == "email_verified":
        return value.lower() == "true"
    return value


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
):
    token = credentials.credentials
    try:
        if os.environ.get("TESTING"):
            # Decode token using HS256 algorithm for testing
            decoded_token = jwt.decode(
                token,
                "test-secret",
                algorithms=["HS256"],
                audience="MockClientId",
                issuer="https://cognito-idp.eu-central-1.amazonaws.com/eu-central-1_MockPoolId",
            )
        else:
            # Get the kid from headers
            headers = jwt.get_unverified_headers(token)
            kid = headers["kid"]

            # Get JWKS and find the public key
            jwks = await get_jwks()
            key = next((key for key in jwks["keys"] if key["kid"] == kid), None)
            if not key:
                raise HTTPException(status_code=401, detail="Public key not found")

            # Construct the public key
            public_key = jwk.construct(key, algorithm="RS256").to_pem()

            # Decode and verify the token
            decoded_token = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=settings.AWS_USER_POOL_CLIENT_ID,
                issuer=f"https://cognito-idp.{settings.AWS_REGION}.amazonaws.com/{settings.AWS_USER_POOL_ID}",
            )
        cognito = get_cognito()
        user = cognito.get_user(token)
        user_attributes_dict = {
            attr["Name"]: _convert_attribute_value(attr["Name"], attr["Value"])
            for attr in user.get("UserAttributes", [])
        }
        # Replace 'cognito:groups' with 'roles'
        roles = decoded_token.pop("cognito:groups", [])
        user_attributes_dict["roles"] = roles
        decoded_token.update(user_attributes_dict)
        return decoded_token
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Not authorized")


def has_roles(required_roles: list):
    """
    Dependency that checks if user roles intersect the required roles.
    Raises HTTP 403 if not authorized.
    """

    def role_checker(current_user=Depends(get_current_user)):
        groups = current_user.get("roles", [])
        if not any(role in groups for role in required_roles):
            raise HTTPException(status_code=403, detail="Access forbidden")

    return role_checker
