"""
This module contains the implementation of the `IndicatorProcessor` class for the `PouetPouetConnector`.
"""

from time import sleep
from datetime import date
from typing import TYPE_CHECKING, override

from connector.converter_to_stix import ConverterToStix
from connectors_sdk import BaseDataProcessor
from connectors_sdk.models import BaseIdentifiedObject
from pouet_pouet_client.api_client import PouetPouetClient

if TYPE_CHECKING:
    from connector.connector_settings import ConnectorSettings
    from connector.connector_state import ConnectorState


class IndicatorProcessor(BaseDataProcessor):
    """
    Indicator processor implementation for the `PouetPouetConnector`.
    This class inherits from `BaseDataProcessor` and is used to process the indicators retrieved
    from the Pouet API before it is ingested into OpenCTI.
    """

    # Override the typing of `BaseDataProcessor` with concrete types
    settings: "ConnectorSettings"
    state: "ConnectorState"

    @override
    def post_init(self):
        """
        Post-initialization method to set up any additional state or perform actions after the processor has been initialized.
        In this case, it initializes the last ingested timestamp from the state.
        """
        self.api_client = PouetPouetClient(
            base_url=self.settings.pouet_pouet.api_base_url,
            api_key=self.settings.pouet_pouet.api_key,
        )
        self.converter_to_stix = ConverterToStix(
            tlp_level=self.settings.pouet_pouet.tlp_level,
        )

    @override
    def collect(self) -> list[dict]:
        """
        Collect data from the Pouet API.
        This method return retrieved data as a generator of dictionaries,
        where each dictionary represents an indicator to be ingested into OpenCTI.
        """
        self.logger.info("Fetching indicators")

        pouet_indicators = self.api_client.get_indicators()

        self.logger.debug(
            "Fetched indicators", {"indicators_count": len(pouet_indicators)}
        )

        return pouet_indicators

    @override
    def transform(self, data: list[dict]) -> list[list[BaseIdentifiedObject]]:
        """
        Transform the collected data into OCTI objects.
        This method takes the raw data collected from the Pouet API and transform it into
        the format expected by OpenCTI for ingestion.
        Returns a generator of lists of `BaseIdentifiedObject`, where each list contains the OCTI objects of one bundle.
        """
        self.logger.info("Transforming indicators into OCTI objects")

        octi_objects = [
            self.converter_to_stix.tlp_marking,
            self.converter_to_stix.author,
        ]

        for pouet_indicator in data:
            sleep(1)  # simulate long running conversion
            octi_indicator = self.converter_to_stix.create_indicator(pouet_indicator)
            octi_objects.append(octi_indicator)

        self.logger.debug(
            "Transformed indicators into OCTI objects",
            {"octi_objects_count": len(octi_objects)},
        )

        return octi_objects

    @override
    def send(self, bundle_objects: list[BaseIdentifiedObject]):
        """
        Send the transformed data to OpenCTI.
        This method takes the transformed data and sends it to OpenCTI using the `send` method of the `BaseDataProcessor`.
        It also updates the state with the last ingested timestamp after sending the data.
        """
        self.work_name = f"Indicators on {date.today().isoformat()}"
        super().send(bundle_objects=bundle_objects)
