"""Test Base API and subclasses."""

from datetime import datetime
import pytest
from typing import Any

from pytest_mock import MockerFixture
from conftest import MockApiFactory
import eodhd_py.base
from eodhd_py.base import EodHistoricalApi


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("test_case"),
    [
        {
            "symbol": "AAPL",
            "interval": "d",
            "order": "a",
            "from_date": None,
            "to_date": None,
            "expected_params": {"period": "d", "order": "a"},
        },
        {
            "symbol": "MSFT",
            "interval": "w",
            "order": "d",
            "from_date": datetime(2023, 1, 1),
            "to_date": datetime(2023, 12, 31),
            "expected_params": {"period": "w", "order": "d", "from": "2023-01-01", "to": "2023-12-31"},
        },
        {
            "symbol": "NVDA",
            "interval": "m",
            "order": "a",
            "from_date": datetime(2020, 1, 1),
            "to_date": datetime(2020, 12, 31),
            "expected_params": {"period": "m", "order": "a", "from": "2020-01-01", "to": "2020-12-31"},
        },
    ],
)
async def test_parameters(mock_api_factory: MockApiFactory, test_case: dict[str, Any]) -> None:
    """Test EodHistoricalApi business logic with various parameter combinations."""
    api, mock_make_request = mock_api_factory.create(
        EodHistoricalApi, mock_response_data=[{"date": "1986-07-24", "close": 30.9888}]
    )

    await api.get_eod_data(
        symbol=test_case["symbol"],
        interval=test_case["interval"],
        order=test_case["order"],
        from_date=test_case["from_date"],
        to_date=test_case["to_date"],
    )

    mock_make_request.assert_called_once_with(f"eod/{test_case['symbol']}", params=test_case["expected_params"])


@pytest.mark.asyncio
async def test_function_calls_validators(mocker: MockerFixture, mock_api_factory: MockApiFactory) -> None:
    """Test that EodHistoricalApi calls validation functions."""
    spy_validate_normalize_symbol = mocker.spy(eodhd_py.base, "validate_normalize_symbol")
    spy_validate_order = mocker.spy(eodhd_py.base, "validate_order")
    spy_validate_period = mocker.spy(eodhd_py.base, "validate_period")

    api, _ = mock_api_factory.create(EodHistoricalApi)
    await api.get_eod_data(symbol="GME", interval="d", order="a")

    spy_validate_normalize_symbol.assert_called_once_with("GME")
    spy_validate_order.assert_called_once_with("a")
    spy_validate_period.assert_called_once_with("d")

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "interval",
    [
        "1m",
        "5m",
        "1h", 
    ],
)
async def test_interval_parameter_invalid_values(interval: str, mock_api_factory: MockApiFactory) -> None:
    """Test that invalid interval values raise appropriate ValueError."""
    api, _ = mock_api_factory.create(EodHistoricalApi)

    with pytest.raises(ValueError, match="Period must be 'd' \\(daily\\), 'w' \\(weekly\\), or 'm' \\(monthly\\)"):
        await api.get_eod_data(symbol="AAPL", interval=interval)
