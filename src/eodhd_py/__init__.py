"""Package allows for querying the EODHD API using an async interface."""

# TODO: Move EodHistoricalApi and IntradayHistoricalApi to their own submodules
from eodhd_py.base import EodhdApi, EodhdApiConfig, EodHistoricalApi, IntradayHistoricalApi

__all__ = (
    "EodHistoricalApi",
    "EodhdApi",
    "EodhdApiConfig",
    "IntradayHistoricalApi",
)
