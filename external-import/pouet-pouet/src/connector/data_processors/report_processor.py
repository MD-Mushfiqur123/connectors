"""
This module contains the implementation of the `ReportProcessor` class for the `PouetPouetConnector`.
"""

from time import sleep
from typing import TYPE_CHECKING, Generator, override

from connector.converter_to_stix import ConverterToStix
from connectors_sdk import BaseDataProcessor
from connectors_sdk.models import BaseIdentifiedObject, Report
from pouet_pouet_client.api_client import PouetPouetClient

if TYPE_CHECKING:
    from connector.connector_settings import ConnectorSettings
    from connector.connector_state import ConnectorState


class ReportProcessor(BaseDataProcessor):
    """
    Report processor implementation for the `PouetPouetConnector`.
    This class inherits from `BaseDataProcessor` and is used to process the reports retrieved
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
    def collect(self) -> Generator[dict, None, None]:
        """
        Collect data from the Pouet API.
        This method return retrieved data as a generator of dictionaries,
        where each dictionary represents a report to be ingested into OpenCTI.
        """
        last_ingested_at = self.state.last_ingested_at

        self.logger.info("Fetching reports with filters", {"since": last_ingested_at})

        pouet_reports = self.api_client.get_reports(since=last_ingested_at)

        self.logger.debug("Fetched reports")

        return pouet_reports

    @override
    def transform(
        self, data: Generator[dict, None, None]
    ) -> Generator[list[BaseIdentifiedObject], None, None]:
        """
        Transform the collected data into OCTI objects.
        This method takes the raw data collected from the Pouet API and transform it into
        the format expected by OpenCTI for ingestion.
        Returns a generator of lists of `BaseIdentifiedObject`, where each list contains the OCTI objects of one bundle.
        """
        self.logger.info("Transforming reports into OCTI objects")

        try:
            for pouet_report in data:
                sleep(1)  # simulate long running conversion
                octi_report = self.converter_to_stix.create_report(pouet_report)

                octi_objects = [
                    self.converter_to_stix.tlp_marking,
                    self.converter_to_stix.author,
                    octi_report,
                ]

                self.logger.debug(
                    "Transformed report into OCTI objects",
                    {
                        "report_name": pouet_report["name"],
                        "octi_objects_count": len(octi_objects),
                    },
                )

                yield octi_objects
        except Exception as e:
            self.logger.error(
                "Error processing reports. Stopping the ingestion, will retry on next run.",
                {"error": str(e)},
            )

    @override
    def send(self, data: Generator[list[BaseIdentifiedObject], None, None]) -> None:  # type: ignore[override]
        """
        Bundle and send the OCTI objects for ingestion to OpenCTI.
        """
        last_report = None

        for octi_objects in data:
            # Call the send method of the BaseDataProcessor to handle the actual sending of data
            self.work_name = f"Reports since {self.state.last_ingested_at.isoformat(timespec='seconds') if self.state.last_ingested_at else 'the beginning'}"
            super().send(bundle_objects=octi_objects)

            # Update the state with custom fields after sending the data to OpenCTI
            bundle_last_report = next(
                (
                    obj
                    for obj in reversed(list(octi_objects))
                    if isinstance(obj, Report)
                ),
                None,
            )
            if bundle_last_report:
                self.logger.debug(
                    "Saving last report info in connector's state",
                    {
                        "report_name": bundle_last_report.name,
                        "report_id": bundle_last_report.id,
                        "report_publication_date": bundle_last_report.publication_date,
                    },
                )
                if (
                    last_report is None
                    or last_report.publication_date
                    < bundle_last_report.publication_date
                ):
                    last_report = bundle_last_report

                    self.state.last_pouet_id = bundle_last_report.id
                    self.state.last_ingested_at = bundle_last_report.publication_date
                    self.state.save()
