"""Base classes for EodhdApi and its endpoints."""

from datetime import datetime
import aiohttp
from typing import cast
from pydantic import BaseModel, Field, ConfigDict
from .utils import validate_normalize_symbol, validate_order, validate_period


class EodhdApiConfig(BaseModel):
    """
    Configuration Class for EodhdApi and its endpoints.

    The session can be shared between multiple endpoint instances.
    Simply pass the same config object to each endpoint instance.
    If this is the case, set `close_session_on_aexit` to False.
    This avoids closing the session when one endpoint instance is closed.

    This requires you to call `await config.session.close()` manually when done.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    api_key: str = Field(pattern=r"^([A-Za-z0-9.]{16,32}|demo)$", default="demo")
    _session: aiohttp.ClientSession | None = None
    close_session_on_aexit: bool = True

    @property
    def session(self) -> aiohttp.ClientSession:
        """Lazily instantiate the aiohttp ClientSession when first accessed."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    @session.setter
    def session(self, value: aiohttp.ClientSession) -> None:
        """Allow setting a custom session if needed."""
        self._session = value


class BaseEodhdApi:
    """Base class for all EodhdApi endpoint classes."""

    def __init__(self, config: EodhdApiConfig | None = None, api_key: str = "") -> None:
        """Initialize with either a config or an api_key."""
        if not config and not api_key:
            raise ValueError("Either config or api_key must be provided")
        self.config = config or EodhdApiConfig(api_key=api_key)
        self.session = self.config.session
        self.BASE_URL = "https://eodhd.com/api"

    async def __aenter__(self) -> "BaseEodhdApi":
        """Enter the asynchronous context manager."""
        return self

    # TODO: handle exceptions
    async def __aexit__(self, *args) -> None:  # type: ignore # noqa
        """Exit the asynchronous context manager and close session."""
        await self.close()

    async def close(self) -> None:
        """Close the shared session."""
        if self.config.close_session_on_aexit and not self.session.closed:
            await self.session.close()

    async def _make_request(  # TODO: Add option to return dataframe?
        self,
        endpoint: str,
        params: dict[str, str] | None = None,
    ) -> dict[str, str | int]:
        """
        Make an HTTP request to the EODHD API.

        Args:
            endpoint: The API endpoint path (e.g., "eod/AAPL")
            params: Optional dictionary of query parameters

        Returns:
            JSON response as a dictionary

        Raises:
            aiohttp.ClientError: If the HTTP request fails
            ValueError: If the response is not valid JSON

        """
        # Prepare parameters
        request_params = params.copy() if params else {}
        request_params["api_token"] = self.config.api_key
        request_params["fmt"] = "json"

        # Construct URL
        url = f"{self.BASE_URL}/{endpoint.strip('/')}"

        # Make request
        async with self.session.request("GET", url, params=request_params) as response:
            response.raise_for_status()  # Raise an exception for bad status codes
            return await response.json()


class EodHistoricalApi(BaseEodhdApi):
    """EodHistoricalApi endpoint class."""

    async def get_eod_data(
        self,
        symbol: str = "AAPL",
        period: str = "d",
        order: str = "a",
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> dict[str, str | int]:
        """
        Get EOD data for a supplied symbol.

        Args:
            symbol: Stock symbol (e.g., "AAPL")
            period: Data period ("d"=daily, "w"=weekly, "m"=monthly)
            order: Order of data ("a"=ascending, "d"=descending)
            from_date: Start date for data
            to_date: End date for data

        Returns:
            JSON response as a dictionary

        """
        params = {
            "period": period,
            "order": order,
        }

        symbol = validate_normalize_symbol(symbol)
        validate_order(order)
        validate_period(period)

        if from_date is not None:
            params["from"] = from_date.strftime("%Y-%m-%d")
        if to_date is not None:
            params["to"] = to_date.strftime("%Y-%m-%d")

        return await self._make_request(f"eod/{symbol}", params=params)


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
        return self

    # TODO: handle exceptions
    async def __aexit__(self, *args) -> None:  # type: ignore # noqa
        """Exit the asynchronous context manager and close session."""
        await self.close()

    async def close(self) -> None:
        """Close the shared session."""
        if self.config.close_session_on_aexit and not self.config.session.closed:
            await self.config.session.close()

    @property
    def eod_historical_api(self) -> EodHistoricalApi:
        """Lazily instantiate and return the EodHistoricalApi client."""
        if "eod_historical_api" not in self._endpoint_instances:
            self._endpoint_instances["eod_historical_api"] = EodHistoricalApi(self.config)
        return cast(EodHistoricalApi, self._endpoint_instances["eod_historical_api"])

    @property
    def intraday_historical_api(self) -> "IntradayHistoricalApi":
        """Lazily instantiate and return the IntradayHistoricalApi client."""
        if "intraday_historical_api" not in self._endpoint_instances:
            from .intraday_historical import IntradayHistoricalApi
            self._endpoint_instances["intraday_historical_api"] = IntradayHistoricalApi(self.config)
        return cast("IntradayHistoricalApi", self._endpoint_instances["intraday_historical_api"])
