"""Intraday Historical Data API endpoint class."""

from datetime import datetime
from .base import BaseEodhdApi
from .utils import validate_normalize_symbol, validate_interval


class IntradayHistoricalApi(BaseEodhdApi):
    """
    IntradayHistoricalApi endpoint class.
    
    Provides access to EODHD's Intraday Historical Data API endpoint,
    which returns historical intraday data for stocks with various time
    intervals (1m, 5m, 1h) and supports date range filtering.
    
    This class inherits from BaseEodhdApi and follows the same patterns
    as other endpoint classes in the library.
    """

    async def get_intraday_data(
        self,
        symbol: str,
        interval: str,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> dict[str, str | int]:
        """
        Get intraday historical data for a supplied symbol.

        Args:
            symbol: Stock symbol (e.g., "AAPL")
            interval: Time interval ("1m", "5m", "1h")
            from_date: Start date for data
            to_date: End date for data

        Returns:
            JSON response as a dictionary containing intraday data

        Raises:
            ValueError: If symbol or interval parameters are invalid
            aiohttp.ClientError: If the HTTP request fails

        """
        params = {
            "interval": interval,
        }

        # Validate parameters
        symbol = validate_normalize_symbol(symbol)
        validate_interval(interval)

        if from_date is not None:
            params["from"] = from_date.strftime("%Y-%m-%d")
        if to_date is not None:
            params["to"] = to_date.strftime("%Y-%m-%d")

        return await self._make_request(f"intraday/{symbol}", params=params)