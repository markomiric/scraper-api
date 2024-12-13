import logging
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

log = logging.getLogger("uvicorn")


class Settings(BaseSettings):
    DYNAMODB_URL: Optional[str] = None
    TABLE_NAME: str = ""
    AWS_DEFAULT_REGION: str
    AWS_USER_POOL_ID: str
    AWS_USER_POOL_CLIENT_ID: str

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.development"),
        _env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> BaseSettings:
    log.info("Loading config settings from the environment...")
    return Settings()
