"""EOD Historical Data API endpoint."""

from datetime import datetime
from .base import BaseEodhdApi
from .utils import validate_normalize_symbol, validate_order, validate_interval


class EodHistoricalApi(BaseEodhdApi):
    """EodHistoricalApi endpoint class."""

    async def get_eod_data(
        self,
        symbol: str,
        interval: str = "d",
        order: str = "a",
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> dict[str, str | int]:
        """
        Get EOD data for a supplied symbol.

        Args:
            symbol: Stock symbol (e.g., "AAPL")
            interval: Data interval ("d"=daily, "w"=weekly, "m"=monthly)
            order: Order of data ("a"=ascending, "d"=descending)
            from_date: Start date for data
            to_date: End date for data

        Returns:
            JSON response as a dictionary

        """
        # Parameter aliasing for backend compatibility
        period = interval

        params = {
            "period": period,
            "order": order,
        }

        symbol = validate_normalize_symbol(symbol)
        validate_order(order)
        validate_interval(period, data_type="eod")

        if from_date is not None:
            params["from"] = from_date.strftime("%Y-%m-%d")
        if to_date is not None:
            params["to"] = to_date.strftime("%Y-%m-%d")

        return await self._make_request(f"eod/{symbol}", params=params)
