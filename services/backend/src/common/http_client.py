import asyncio
import logging
import random
from dataclasses import dataclass
from functools import wraps
from itertools import cycle
from typing import Any, Callable, Dict, List, Optional, TypeVar

from aiohttp import (
    BasicAuth,
    ClientError,
    ClientSession,
    ClientTimeout,
    ServerConnectionError,
    ServerTimeoutError,
)
from bs4 import BeautifulSoup


@dataclass
class ProxyConfig:
    """Configuration for HTTP/HTTPS proxies with authentication support."""

    proxies: str
    username: Optional[str] = None
    password: Optional[str] = None

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.proxies:
            raise ValueError("Proxy list cannot be empty")

        if bool(self.username) != bool(self.password):
            raise ValueError("Both username and password must be provided or neither")

    @property
    def proxy_list(self) -> List[str]:
        """Returns list of configured proxies."""
        return [proxy.strip() for proxy in self.proxies.split(",") if proxy.strip()]

    def get_proxy_url(self, proxy: str) -> str:
        """Returns proxy URL with authentication if configured."""
        if self.username and self.password:
            if "://" in proxy:
                protocol = proxy.split("://")[0]
                host = proxy.split("://")[1]
                return f"{protocol}://{self.username}:{self.password}@{host}"
            return f"http://{self.username}:{self.password}@{proxy}"
        return proxy

    def get_auth(self) -> Optional[BasicAuth]:
        """Returns BasicAuth object if credentials are configured."""
        if self.username and self.password:
            return BasicAuth(self.username, self.password)
        return None


T = TypeVar("T")


def async_retry_with_backoff(
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2,
    jitter: bool = True,
):
    """
    Decorator for async functions to retry with exponential backoff.

    Args:
        max_retries: Maximum number of retries before giving up
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential calculation
        jitter: Whether to add random jitter to delay
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            retries = 0
            while True:
                try:
                    return await func(*args, **kwargs)

                except (
                    ClientError,
                    ServerConnectionError,
                    ServerTimeoutError,
                    asyncio.TimeoutError,
                ) as e:
                    retries += 1

                    if retries > max_retries:
                        logging.error(
                            f"Max retries ({max_retries}) exceeded. Last error: {str(e)}"
                        )
                        return

                    # Calculate delay with exponential backoff
                    delay = min(
                        base_delay * (exponential_base ** (retries - 1)), max_delay
                    )

                    # Add jitter if enabled
                    if jitter:
                        delay = delay * (0.5 + random.random())

                    logging.warning(
                        f"Attempt {retries}/{max_retries} failed. "
                        f"Retrying in {delay:.2f}s. Error: {str(e)}"
                    )

                    await asyncio.sleep(delay)

                except Exception as e:
                    # Don't retry on unhandled exceptions
                    logging.error(f"Unhandled exception occurred: {str(e)}")
                    raise

        return wrapper

    return decorator


class HttpClient:
    def __init__(self, proxy_config: Optional[ProxyConfig] = None, timeout: int = 30):
        self.proxy_config = proxy_config
        self.timeout = ClientTimeout(total=timeout)
        self._proxy_cycle = cycle(proxy_config.proxy_list) if proxy_config else None
        self._session = ClientSession(trust_env=True)

    def _get_next_proxy(self) -> Optional[Dict[str, str]]:
        if not self._proxy_cycle or not self.proxy_config:
            return None
        proxy = next(self._proxy_cycle)
        return self.proxy_config.get_proxy_url(proxy)

    @async_retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=3.0, jitter=True)
    async def get(self, url: str) -> Optional[BeautifulSoup]:
        proxy = self._get_next_proxy()
        try:
            response = await self._session.get(url, proxy=proxy, ssl=False)
            response.raise_for_status()
            content = await response.text()
            return BeautifulSoup(content, "html.parser")
        except ClientError as e:
            logging.warning(f"Proxy {proxy} failed: {str(e)}")
            raise

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
