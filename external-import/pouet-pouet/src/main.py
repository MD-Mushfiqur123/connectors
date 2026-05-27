"""
Entry point of the script

- traceback.print_exc(): This function prints the traceback of the exception to the standard error (stderr).
The traceback includes information about the point in the program where the exception occurred,
which is very useful for debugging purposes.
- exit(1): effective way to terminate a Python program when an error is encountered.
It signals to the operating system and any calling processes that the program did not complete successfully.
"""

import traceback

from connector import (
    ConnectorSettings,
    ConnectorState,
    IndicatorProcessor,
    ReportProcessor,
)
from connectors_sdk import ExternalImportConnector as PouetPouetConnector
from connectors_sdk import logger

if __name__ == "__main__":
    try:
        logger.info("Starting process")

        settings = ConnectorSettings()
        state = ConnectorState()

        report_processor = ReportProcessor()
        indicator_processor = IndicatorProcessor()

        connector = PouetPouetConnector(
            settings=settings,
            state=state,
            data_processors=[
                report_processor,
                indicator_processor,
            ],
        )
        connector.start()
    except Exception as e:
        logger.error("Unexpected error occurred", {"error": str(e)})

        traceback.print_exc()

        logger.error("Killing process (exit code 1)")

        exit(1)
