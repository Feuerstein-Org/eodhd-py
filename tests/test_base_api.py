"""Test Base class"""

import pytest
from aioresponses import aioresponses
from eodhd_py.base import BaseEodhdApi, EodhdApiConfig, EodHistoricalApi, IntradayHistoricalApi, EodhdApi, UserApi
import aiohttp
from typing import Any
from urllib.parse import urlencode

# API endpoints to test for lazy loading and shared session
# Each tuple contains the property name used for lazy loading and the corresponding class
API_ENDPOINTS = [
    ("eod_historical_api", EodHistoricalApi),
    ("intraday_historical_api", IntradayHistoricalApi),
    ("user_api", UserApi),
]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("config", "api_key", "error"),
    [
        (EodhdApiConfig(api_key="demo"), "", None),
        (None, "demo", None),
        (None, "", ValueError),
    ],
)
async def test_base_eodhdapi_init(config: EodhdApiConfig | None, api_key: str, error: type[ValueError] | None) -> None:
    """Test initialization of BaseEodhdApi with various config and api_key combinations."""
    if error:
        with pytest.raises(error, match="Either config or api_key must be provided"):
            BaseEodhdApi(config=config, api_key=api_key)
    else:
        api = BaseEodhdApi(config=config, api_key=api_key)
        assert api.config is not None
        assert api.session is not None
        assert api.BASE_URL == "https://eodhd.com/api"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("endpoint", "params", "expected_response", "expected_url_params"),
    [
        ("eod/AAPL", {"period": "d", "order": "a"}, {"data": "aapl_daily"}, {"period": "d", "order": "a"}),
        ("eod/GOOG", {"period": "w"}, {"data": "goog_weekly"}, {"period": "w"}),
        ("eod/MSFT", None, {"data": "msft_default"}, {}),
        ("eod/TSLA", {}, {"data": "tsla_empty"}, {}),
        (
            "eod/NVDA",
            {"period": "m", "order": "d", "from": "2023-01-01"},
            {"data": "nvda_monthly"},
            {"period": "m", "order": "d", "from": "2023-01-01"},
        ),
        ("/eod/AMD/", {"period": "d"}, {"data": "amd_daily"}, {"period": "d"}),
        ("fundamentals/AMZN", {"filter": "General"}, {"fundamentals": "amazon_data"}, {"filter": "General"}),
    ],
)
async def test_make_request_parameters(
    endpoint: str, params: dict[str, str], expected_response: dict[str, str], expected_url_params: dict[str, str]
) -> None:
    """Test that _make_request passes parameters correctly with various inputs."""
    # Create a real aiohttp session
    session = aiohttp.ClientSession()

    try:
        # Create config with the real session
        config = EodhdApiConfig()
        config.session = session

        # Use aioresponses to mock the HTTP response
        with aioresponses() as mock_http:
            base_url = "https://eodhd.com/api"
            clean_endpoint = endpoint.strip("/")  # In the real code it also gets stripped

            # api_token and fmt are always added
            all_params = {"api_token": "demo", "fmt": "json"}
            if params:
                all_params.update(params)

            expected_url = f"{base_url}/{clean_endpoint}?{urlencode(all_params)}"

            mock_http.get(expected_url, payload=expected_response)  # type: ignore

            api = BaseEodhdApi(config=config)
            result = await api._make_request(endpoint, params)

            assert result == expected_response

            requests_dict: dict[Any, Any] = mock_http.requests  # type: ignore
            assert len(requests_dict) == 1

            # Extract info for testing
            request_key, request_calls = next(iter(requests_dict.items()))
            method, actual_url = request_key
            request_call = request_calls[0]

            assert method == "GET"
            assert f"{base_url}/{clean_endpoint}" in str(actual_url)

            request_params = request_call.kwargs["params"]
            assert request_params["api_token"] == "demo"
            assert request_params["fmt"] == "json"

            # Check all expected additional parameters
            for param_key, param_value in expected_url_params.items():
                assert request_params[param_key] == param_value

            # Ensure no unexpected parameters were added
            expected_param_count = 2 + len(expected_url_params)  # 2 for api_token and fmt
            assert len(request_params) == expected_param_count

    finally:
        await session.close()


@pytest.mark.asyncio
@pytest.mark.parametrize(("api_property_name", "api_class"), API_ENDPOINTS)
async def test_lazy_loading_property(api_property_name: str, api_class: type) -> None:
    """Test lazy loading of API endpoint properties."""
    config = EodhdApiConfig(api_key="demo")
    api = EodhdApi(config=config)

    # Property should not exist in _endpoint_instances initially
    assert api_class.__name__ not in api._endpoint_instances

    # First access should create the instance
    endpoint_instance = getattr(api, api_property_name)
    assert isinstance(endpoint_instance, api_class)
    assert api_class.__name__ in api._endpoint_instances

    # Second access should return the same instance
    endpoint_instance2 = getattr(api, api_property_name)
    assert endpoint_instance is endpoint_instance2


@pytest.mark.asyncio
async def test_shared_session_usage() -> None:
    """Test that endpoint instances share the same session and configuration."""
    config = EodhdApiConfig(api_key="demo")
    api = EodhdApi(config=config)

    # Get all available endpoint instances
    endpoint_instances: list[BaseEodhdApi] = []
    for prop_name, _ in API_ENDPOINTS:
        endpoint_instances.append(getattr(api, prop_name))

    # All endpoints should share the same session and config
    # Compare each endpoint to the first one
    first_endpoint = endpoint_instances[0]
    for endpoint in endpoint_instances[1:]:
        assert endpoint.session is first_endpoint.session
        assert endpoint.config is first_endpoint.config


@pytest.mark.asyncio
@pytest.mark.parametrize(("api_property_name", "api_class"), API_ENDPOINTS)
async def test_async_context_manager_behavior(api_property_name: str, api_class: type) -> None:
    """Test async context manager behavior for API endpoints."""
    config = EodhdApiConfig(api_key="demo", close_session_on_aexit=True)

    async with EodhdApi(config=config) as api:
        endpoint_instance = getattr(api, api_property_name)
        assert not endpoint_instance.session.closed

    # Session should be closed after exiting context
    assert endpoint_instance.session.closed
