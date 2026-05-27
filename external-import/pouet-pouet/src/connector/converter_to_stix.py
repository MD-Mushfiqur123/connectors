from datetime import datetime, timezone
from typing import Literal, ClassVar

from connectors_sdk import logger as connector_logger
from connectors_sdk.models import Indicator, OrganizationAuthor, Report, TLPMarking
from pycti import OpenCTIConnectorHelper


class ConverterToStix:
    """
    Provides methods for converting various types of input data into STIX 2.1 objects.

    REQUIREMENTS:
        - `generate_id()` methods from `pycti` library MUST be used to generate the `id` of each entity (except observables),
        e.g. `pycti.Identity.generate_id(name="Source Name", identity_class="organization")` for a STIX Identity.
    """

    logger: ClassVar = connector_logger.get_child("ConverterToStix")

    def __init__(
        self,
        tlp_level: Literal[
            "clear",
            "white",
            "green",
            "amber",
            "amber+strict",
            "red",
        ],
    ):
        """
        Initialize the converter with necessary configuration.
        Other arguments CAN be added (e.g. `tlp_level`) if necessary.

        Args:
            tlp_level (str): The TLP level to add to the created STIX entities.
        """

        self.author = self.create_author()
        self.tlp_marking = self.create_tlp_marking(level=tlp_level.lower())

    def create_author(self) -> OrganizationAuthor:
        self.logger.debug("Creating OrganizationAuthor")

        return OrganizationAuthor(
            name="Pouet Pouet",
            description="Pouet Pouet is a platform for pouetpoueting.",
        )

    def create_tlp_marking(self, level):
        self.logger.debug("Creating TLPMarking", {"level": level})

        return TLPMarking(level=level)

    def create_report(self, report_data: dict) -> Report:
        self.logger.debug("Creating Report", {"report_data": report_data})

        return Report(
            name=report_data["name"],
            publication_date=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            author=self.author,
            markings=[self.tlp_marking],
        )

    def create_indicator(self, indicator_data: dict) -> Indicator:
        self.logger.debug("Creating Indicator", {"indicator_data": indicator_data})

        indicator_type = indicator_data["type"]
        indicator_name = indicator_data["name"]

        return Indicator(
            name=indicator_name,
            pattern_type="stix",
            pattern=f"[{indicator_type}:value = '{indicator_name}']",
            valid_from=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            author=self.author,
            markings=[self.tlp_marking],
        )
