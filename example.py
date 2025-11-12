"""Sample EODHD API usage."""

from eodhd_py.base import EodhdApi
import asyncio
import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


async def main() -> None:
    """Main function to demonstrate EODHD API usage."""
    async with EodhdApi() as api:
        data = await api.eod_historical_api.get_eod_data(order="d", symbol="MSFT", interval="d")
        logging.info("Retrieved EOD data: %s", data)
    logging.info("Done")


asyncio.run(main())
