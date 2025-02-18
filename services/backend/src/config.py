import logging
from functools import lru_cache
from typing import Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

log = logging.getLogger("uvicorn")


class Settings(BaseSettings):
    DYNAMODB_URL: Optional[str] = None
    TABLE_NAME: str = ""
    AWS_REGION: str = "eu-central-1"
    AWS_USER_POOL_ID: str = ""
    AWS_USER_POOL_CLIENT_ID: str = ""
    PROXIES: str = ""
    PROXY_USERNAME: str = ""
    PROXY_PASSWORD: str = ""
    TIMESPAN: str = "r2592000"
    PAGES_TO_SCRAPE: int = 10
    ROUNDS: int = 1
    DAYS_TO_SCRAPE: int = 10
    REQUEST_DELAY: int = 1
    TIMEOUT: int = 5
    OPENAI_API_KEY: str = ""
    AUTHOR: str = "Anonymous"

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.development"),
        _env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_proxy_config(self):
        if any([self.PROXY_USERNAME, self.PROXY_PASSWORD]) and not all(
            [self.PROXY_USERNAME, self.PROXY_PASSWORD]
        ):
            raise ValueError(
                "Both PROXY_USERNAME and PROXY_PASSWORD must be provided if one is set"
            )
        return self


@lru_cache()
def get_settings() -> BaseSettings:
    log.info("Loading config settings from the environment...")
    return Settings()
