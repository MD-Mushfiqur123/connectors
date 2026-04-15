"""Tests for SDKLogger singleton."""

import logging
import logging.handlers
from unittest.mock import MagicMock

import pytest
from connectors_sdk.logging.sdk_logger import SDKLogger, sdk_logger

_SDK_LOGGER_NAME = "connectors_sdk"


@pytest.fixture(autouse=True)
def reset_sdk_logger():
    """Reset the SDKLogger singleton and all affected stdlib loggers between tests."""
    yield
    # Reset singleton
    SDKLogger._instance = None
    # Reset SDK logger
    sdk_logger = logging.getLogger(_SDK_LOGGER_NAME)
    sdk_logger.handlers.clear()
    sdk_logger.filters.clear()
    # Reset any connector_name loggers registered during tests
    for name in list(logging.Logger.manager.loggerDict):
        if name in ("fake_connector", "another_connector"):
            logger = logging.getLogger(name)
            logger.handlers.clear()
            logger.filters.clear()
            logger.propagate = True
            logger.parent = logging.getLogger()


@pytest.fixture
def mock_helper() -> MagicMock:
    """Return a mock OpenCTIConnectorHelper."""
    helper = MagicMock()
    helper.connect_name = "fake_connector"
    helper.log_level = "debug"
    return helper


@pytest.fixture
def fresh_sdk_logger() -> SDKLogger:
    """Return a fresh SDKLogger singleton (after reset)."""
    return SDKLogger()


class TestSDKLoggerSingleton:
    def test_same_instance(self, fresh_sdk_logger: SDKLogger) -> None:
        assert SDKLogger() is fresh_sdk_logger

    def test_module_level_sdk_logger_is_instance(self) -> None:
        assert isinstance(sdk_logger, SDKLogger)

    def test_logger_name_is_connectors_sdk(self, fresh_sdk_logger: SDKLogger) -> None:
        assert fresh_sdk_logger._logger.name == _SDK_LOGGER_NAME

    def test_default_level_is_info(self, fresh_sdk_logger: SDKLogger) -> None:
        assert fresh_sdk_logger._logger.level == logging.INFO

    def test_propagate_disabled(self, fresh_sdk_logger: SDKLogger) -> None:
        assert fresh_sdk_logger._logger.propagate is False

    def test_console_handler_present(self, fresh_sdk_logger: SDKLogger) -> None:
        assert any(
            isinstance(h, logging.StreamHandler)
            for h in fresh_sdk_logger._logger.handlers
        )
