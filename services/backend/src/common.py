from typing import Union

import jwt
from fastapi import Header, HTTPException

from src.config import get_settings

config = get_settings()


def get_user_email(authorization: Union[str, None] = Header(default=None)) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        token = authorization.replace("Bearer ", "").encode("utf-8")

        payload = jwt.decode(token, options={"verify_signature": False})

        if "cognito:username" not in payload:
            raise HTTPException(status_code=401, detail="Invalid token format")

        return payload["cognito:username"]

    except jwt.DecodeError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
