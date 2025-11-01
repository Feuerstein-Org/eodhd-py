"""Tests for IntradayHistoricalApi endpoint class."""

from datetime import datetime
import pytest
from typing import Any

from pytest_mock import MockerFixture
from conftest import MockApiFactory
import eodhd_py.base
from eodhd_py.base import IntradayHistoricalApi
from eodhd_py.utils import validate_normalize_symbol


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("test_case"),
    [
        {
            "symbol": "AAPL",
            "interval": "1m",
            "from_date": None,
            "to_date": None,
            "expected_params": {"interval": "1m"},
        },
        {
            "symbol": "MSFT",
            "interval": "5m",
            "from_date": datetime(2023, 1, 1),
            "to_date": datetime(2023, 12, 31),
            "expected_params": {"interval": "5m", "from": "2023-01-01", "to": "2023-12-31"},
        },
        {
            "symbol": "NVDA",
            "interval": "1h",
            "from_date": datetime(2020, 1, 1),
            "to_date": None,
            "expected_params": {"interval": "1h", "from": "2020-01-01"},
        },
        {
            "symbol": "BRK.B.US",
            "interval": "1m",
            "from_date": None,
            "to_date": datetime(2023, 6, 30),
            "expected_params": {"interval": "1m", "to": "2023-06-30"},
        },
    ],
)
async def test_parameters(mock_api_factory: MockApiFactory, test_case: dict[str, Any]) -> None:
    """Test IntradayHistoricalApi business logic with various parameter combinations."""
    api, mock_make_request = mock_api_factory.create(
        IntradayHistoricalApi, mock_response_data=[{"datetime": "2023-01-01 09:30:00", "close": 150.75}]
    )

    await api.get_intraday_data(
        symbol=test_case["symbol"],
        interval=test_case["interval"],
        from_date=test_case["from_date"],
        to_date=test_case["to_date"],
    )

    expected_symbol = validate_normalize_symbol(test_case["symbol"])
    mock_make_request.assert_called_once_with(f"intraday/{expected_symbol}", params=test_case["expected_params"])


@pytest.mark.asyncio
async def test_function_calls_validators(mocker: MockerFixture, mock_api_factory: MockApiFactory) -> None:
    """Test that IntradayHistoricalApi calls validation functions."""
    spy_validate_normalize_symbol = mocker.spy(eodhd_py.base, "validate_normalize_symbol")
    spy_validate_interval = mocker.spy(eodhd_py.base, "validate_interval")

    api, _ = mock_api_factory.create(IntradayHistoricalApi)
    await api.get_intraday_data(symbol="GME", interval="5m")

    spy_validate_normalize_symbol.assert_called_once_with("GME")
    spy_validate_interval.assert_called_once_with("5m")
