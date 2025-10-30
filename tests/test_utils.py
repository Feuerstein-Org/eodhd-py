"""Tests for utility functions in eodhd_py.utils."""

import pytest
from eodhd_py.utils import validate_normalize_symbol, validate_order, validate_period, validate_interval
import re


@pytest.mark.parametrize(
    ("symbol", "expected"),
    [
        ("AAPL", "AAPL"),
        ("GOOG", "GOOG"),
        ("BRK.B.US", "BRK-B.US"),
        ("BRK-A", "BRK-A"),
        ("SPY", "SPY"),
    ],
)
def test_validate_normalize_symbol_valid(symbol: str, expected: str) -> None:
    """Test valid symbols."""
    assert validate_normalize_symbol(symbol) == expected


@pytest.mark.parametrize(
    ("symbol"),
    [
        "INVALID SYMBOL!",
        "",
        "A" * 49,  # Too long
        "symbol with spaces",
        "symbol@invalid",
    ],
)
def test_validate_normalize_symbol_invalid(symbol: str) -> None:
    """Test invalid symbols."""
    with pytest.raises(ValueError, match="Symbol is invalid"):
        validate_normalize_symbol(symbol)


@pytest.mark.parametrize("order", ["a", "d"])
def test_validate_order_valid(order: str) -> None:
    """Test valid order values."""
    assert validate_order(order) is True


@pytest.mark.parametrize(
    "order",
    [
        "x",
        "ascending",
        "descending",
        "A",
        "D",
    ],
)
def test_validate_order_invalid(order: str) -> None:
    """Test invalid order values."""
    with pytest.raises(ValueError, match=re.escape("Order must be 'a' (ascending) or 'd' (descending)")):
        validate_order(order)


@pytest.mark.parametrize("period", ["d", "w", "m"])
def test_validate_period_valid(period: str) -> None:
    """Test valid period values."""
    assert validate_period(period) is True


@pytest.mark.parametrize(
    "period",
    [
        "x",
        "daily",
        "weekly",
        "monthly",
        "D",
        "W",
        "M",
    ],
)
def test_validate_period_invalid(period: str) -> None:
    """Test invalid period values."""
    with pytest.raises(ValueError, match=re.escape("Period must be 'd' (daily), 'w' (weekly), or 'm' (monthly)")):
        validate_period(period)


@pytest.mark.parametrize("interval", ["1m", "5m", "1h"])
def test_validate_interval_valid(interval: str) -> None:
    """Test valid interval values."""
    assert validate_interval(interval) is True


@pytest.mark.parametrize(
    "interval",
    [
        "1s",
        "10m",
        "2h",
        "1M",
        "5M",
        "1H",
    ],
)
def test_validate_interval_invalid(interval: str) -> None:
    """Test invalid interval values."""
    with pytest.raises(ValueError, match=re.escape("Interval must be '1m', '5m', or '1h'")):
        validate_interval(interval)
