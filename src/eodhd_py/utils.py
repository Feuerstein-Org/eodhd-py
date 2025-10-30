"""General validation functions."""

from re import compile as re_compile


def validate_normalize_symbol(symbol: str) -> str:
    """Validate and format a stock symbol for EODHD API."""
    IS_MARKET = symbol.count(".") == 2  # noqa: PLR2004

    # Validate symbol
    regex = re_compile(r"^[A-z0-9-$\.+]{1,48}$")
    if not regex.match(symbol):
        raise ValueError(f"Symbol is invalid: {symbol}")

    # replace "." with "-" in markets
    if IS_MARKET:
        symbol = symbol.replace(".", "-", 1)  # TODO: Check when this happens
    return symbol


def validate_order(order: str) -> bool:
    """Validate order parameter."""
    if order not in ("a", "d"):
        raise ValueError("Order must be 'a' (ascending) or 'd' (descending)")
    return True


def validate_period(period: str) -> bool:
    """Validate period parameter."""
    if period not in ("d", "w", "m"):
        raise ValueError("Period must be 'd' (daily), 'w' (weekly), or 'm' (monthly)")
    return True
