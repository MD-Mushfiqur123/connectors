"""SDK-wide singleton logger used for logging inside the connectors-sdk."""

from connectors_sdk.logging._base_logger import BaseLogger


class SDKLogger(BaseLogger):
    """Singleton SDK logger, parent of all loggers inside the connectors-sdk.
    Logs immediately to stderr via a `StreamHandler` using `CustomJsonFormatter` (same format as pycti's logger).
    /!\\ This logger is intended to log internally within the connectors-sdk,
    it shouldn't be used by connectors directly (for that, see `ConnectorLogger`).

    Usage:
        # Anywhere in the connectors-sdk codebase, at any time:
        from connectors_sdk import SDKLogger
        logger = SDKLogger()
        logger.info("Works before pycti is ready")
    """

    _instance: "SDKLogger | None" = None

    def __new__(cls) -> "SDKLogger":
        """Ensure only one instance of SDKLogger exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Set up logger with the default `StreamHandler` handler."""
        # Log level is set to INFO by default, but will be overridden
        # to match OpenCTIConnectorHelper's log level once it's available.
        super().__init__(name="connectors_sdk", level="info")


# For convenience, this module provides a default logger instance,
# but `SDKLogger` can also be instantiated directly if needed (e.g. for testing purpose).
sdk_logger = SDKLogger()
