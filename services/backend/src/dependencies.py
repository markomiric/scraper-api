import os

import requests
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwk, jwt

from src.aws.cognito import Cognito
from src.config import get_settings
from src.job.store import JobStore

settings = get_settings()
bearer_scheme = HTTPBearer()

# Cache the JWKS for token verification
jwks_url = f"https://cognito-idp.{settings.AWS_REGION}.amazonaws.com/{settings.AWS_USER_POOL_ID}/.well-known/jwks.json"
jwks = requests.get(jwks_url).json()


def get_current_user(
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

            # Find the public key in JWKS
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
        return decoded_token
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def has_roles(required_roles: list):
    def role_checker(current_user=Depends(get_current_user)):
        groups = current_user.get("cognito:groups", [])
        if not any(role in groups for role in required_roles):
            raise HTTPException(status_code=403, detail="Access forbidden")

    return role_checker


def get_job_store() -> JobStore:
    return JobStore(settings.TABLE_NAME, dynamodb_url=settings.DYNAMODB_URL)


def get_cognito() -> Cognito:
    return Cognito(
        region_name=settings.AWS_REGION,
        user_pool_id=settings.AWS_USER_POOL_ID,
        user_pool_client_id=settings.AWS_USER_POOL_CLIENT_ID,
    )
