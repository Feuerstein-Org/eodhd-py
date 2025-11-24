"""Sample EODHD API usage."""

from eodhd_py import EodhdApi, EodhdApiConfig
import asyncio
import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


async def main() -> None:
    """Main function to demonstrate EODHD API usage."""
    # Example 1
    async with EodhdApi() as api:
        data = await api.eod_historical_api.get_eod_data(order="d", symbol="MSFT", interval="d")
        logging.info("Retrieved EOD data: %s", len(data))

    # Example 2
    # Using custom configuration
    config = EodhdApiConfig(
        api_key="demo",
        max_retries=5,
        daily_max_sleep=1800,  # Wait max 30 minutes for daily limit
        minute_max_sleep=60,  # Wait max 60 seconds for minute limit
        # Note: setting the below is not recommended since the client auto-handles rate limits
        # daily_calls_rate_limit=50000,  # 50k requests per day
        # daily_remaining_limit=10000,  # 10k remaining requests
        # minute_requests_rate_limit=500,  # 500 requests per minute
        # minute_remaining_limit=100,  # 100 remaining requests
        # extra_limit=10,  # 10 extra non-refilling requests
    )
    async with EodhdApi(config=config) as api:
        eod_data = await api.eod_historical_api.get_eod_data(symbol="AAPL", interval="d")
        logging.info("EOD data retrieved: %s", len(eod_data))

        intraday_data = await api.intraday_historical_api.get_intraday_data(symbol="TSLA", interval="5m")
        logging.info("Intraday data retrieved: %s", len(intraday_data))

    logging.info("Done")


asyncio.run(main())
