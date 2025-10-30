"""Test fixtures for API client tests."""

from typing import TypeVar, Any
from dataclasses import dataclass
from unittest.mock import AsyncMock
from eodhd_py.base import BaseEodhdApi, EodhdApiConfig
from pytest_mock import MockerFixture
import aiohttp
import pytest


@dataclass
class MockApiConfig:
    """Shared configuration for all API mocking."""

    api_key: str = "demo"
    close_session_on_aexit: bool = True
    # Test specific options
    mock_response_data: dict[str, Any] | None = None
    mock_status_code: int = 200
    mock_raise_for_status: bool = False


# This class will be removed in the next commit - it's basically useless for now
# In `test_base_api.py`, we will directly use BaseEodhdApi and mock aiohttp
class MockBaseEodhdApi(BaseEodhdApi):
    """
    Mock implementation for unit testing BaseEodhdApi itself.

    Use this when testing the base class methods like _make_request.
    """

    def __init__(self, mocker: MockerFixture, config: MockApiConfig) -> None:
        """Ingest mock config and initialize real config, additionally mock session."""
        # Create real config for parent
        real_config = EodhdApiConfig(
            api_key=config.api_key,
            close_session_on_aexit=config.close_session_on_aexit,
        )

        self.test_config = config

        # Create mock response
        self.mock_response = mocker.AsyncMock()
        self.mock_response.json = mocker.AsyncMock(return_value=config.mock_response_data or {})
        self.mock_response.status = config.mock_status_code

        if config.mock_raise_for_status:
            self.mock_response.raise_for_status = mocker.MagicMock(side_effect=aiohttp.ClientError("Mock error"))
        else:
            self.mock_response.raise_for_status = mocker.MagicMock()

        # Create mock session
        self.mock_session = mocker.AsyncMock()
        self.mock_session.request = mocker.AsyncMock(return_value=self.mock_response)
        self.mock_session.closed = False
        self.mock_session.close = mocker.AsyncMock()

        # Initialize parent and replace session
        super().__init__(config=real_config)
        self.session = self.mock_session
        self.config.session = self.mock_session


# Factories

T = TypeVar("T", bound=BaseEodhdApi)


class MockApiFactory:
    """
    Factory for testing subclasses that inherit from BaseEodhdApi.

    Creates real instances but mocks the _make_request method.
    Use this when testing EodHistoricalApi, etc.
    """

    def __init__(self, mocker: MockerFixture) -> None:
        """Initialize with pytest-mock's mocker fixture."""
        self.mocker = mocker

    def create(self, api_class: type[T], config: MockApiConfig | None = None, **kwargs: Any) -> tuple[T, AsyncMock]:
        """
        Create a mock instance of any API subclass.

        kwargs will be passed to config if config is None.
        """
        if config is None:
            config = MockApiConfig(**kwargs)

        # Create real config and instance
        real_config = EodhdApiConfig(api_key=config.api_key, close_session_on_aexit=config.close_session_on_aexit)
        instance = api_class(config=real_config)

        # Mock only _make_request
        mock_make_request = self.mocker.AsyncMock(return_value=config.mock_response_data or {})

        if config.mock_raise_for_status:
            mock_make_request.side_effect = aiohttp.ClientError("Mock error")

        instance._make_request = mock_make_request

        return instance, mock_make_request


class MockBaseEodhdApiFactory:
    """Factory for creating MockBaseEodhdApi instances."""

    def __init__(self, mocker: MockerFixture) -> None:
        """Initialize mocker."""
        self._mocker = mocker

    def create(self, config: MockApiConfig | None = None, **kwargs: Any) -> MockBaseEodhdApi:
        """
        Create a MockBaseEodhdApi instance.

        kwargs will be passed to config if config is None.
        """
        if config is None:
            config = MockApiConfig(**kwargs)
        return MockBaseEodhdApi(self._mocker, config)


# Fixtures
@pytest.fixture
def mock_base_eodhd_api_factory(mocker: MockerFixture) -> MockBaseEodhdApiFactory:
    """For unit testing BaseEodhdApi methods."""
    return MockBaseEodhdApiFactory(mocker)


@pytest.fixture
def mock_api_factory(mocker: MockerFixture) -> MockApiFactory:
    """For integration testing of subclasses."""
    return MockApiFactory(mocker)
