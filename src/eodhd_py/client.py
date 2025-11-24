"""Main EODHD API client."""

from typing import cast
from .base import BaseEodhdApi, EodhdApiConfig
from .eod_historical import EodHistoricalApi
from .intraday_historical import IntradayHistoricalApi
from .user import UserApi


class EodhdApi:
    """
    EODHD API Client Class

    This class serves as the main entry point for interacting with various EODHD API endpoints.
    Either pass a EodhdApiConfig object or an api_key string to the constructor.

    After instantiation, access specific API endpoints via properties.
    E.g. `api.eod_historical_api`.
    """

    def __init__(self, config: EodhdApiConfig | None = None, api_key: str = "demo") -> None:
        """Initialize the EodhdApi client with either a config or an api_key."""
        self.config = config or EodhdApiConfig(api_key=api_key)
        self._endpoint_instances: dict[str, BaseEodhdApi] = {}

    async def __aenter__(self) -> "EodhdApi":
        """Enter the asynchronous context manager."""
        # Increment reference count for session usage
        self.config.increment_session_ref()
        return self

    # TODO: handle exceptions
    async def __aexit__(self, *args) -> None:  # type: ignore # noqa
        """Exit the asynchronous context manager and close session if no other instances are using it."""
        # Decrement reference count
        self.config.decrement_session_ref()
        # Only close session when no more references exist
        if self.config.should_close_session() and not self.config.session.closed:
            await self.config.session.close()

    def _get_endpoint(self, endpoint_class: type[BaseEodhdApi]) -> BaseEodhdApi:
        """Generic endpoint getter to reduce boilerplate."""
        key = endpoint_class.__name__
        if key not in self._endpoint_instances:
            self._endpoint_instances[key] = endpoint_class(self.config)
        return self._endpoint_instances[key]

    @property
    def eod_historical_api(self) -> EodHistoricalApi:
        """EodHistoricalApi client."""
        return cast(EodHistoricalApi, self._get_endpoint(EodHistoricalApi))

    @property
    def intraday_historical_api(self) -> IntradayHistoricalApi:
        """IntradayHistoricalApi client."""
        return cast(IntradayHistoricalApi, self._get_endpoint(IntradayHistoricalApi))

    @property
    def user_api(self) -> "UserApi":
        """UserApi client."""
        return cast(UserApi, self._get_endpoint(UserApi))
