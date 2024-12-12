import logging
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings

log = logging.getLogger("uvicorn")


class Settings(BaseSettings):
    TABLE_NAME: str = ""
    DYNAMODB_URL: Optional[str] = None


@lru_cache()
def get_settings() -> BaseSettings:
    log.info("Loading config settings from the environment...")
    return Settings()
