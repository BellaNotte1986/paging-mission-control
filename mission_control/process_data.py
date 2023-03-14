import datetime as dt
import enum
import typing
from collections.abc import Iterable, Sequence
from dataclasses import dataclass


class Component(enum.StrEnum):
    """Represents the different component types."""

    BATT = "BATT"
    TSTAT = "TSTAT"


class Alert(typing.TypedDict):
    """Represents an alert to be emitted."""

    satelliteId: int
    severity: str
    component: str
    timestamp: dt.datetime


@dataclass
class Record:
    """Represents a single data entry read from the input file."""

    timestamp: dt.datetime
    satellite_id: int
    red_high: int
    yellow_high: int
    yellow_low: int
    red_low: int
    val: float
    component: Component


AlertCallback = typing.Callable[[Sequence[Record]], Alert | None]


class RecordProcessor:
    """Processes records and returns warnings if necessary."""

    def __init__(self):
        self.data: dict[int, list[Record]] = {}
        self.alerts: dict[
            Component, list[AlertCallback]
        ] = {}
        # can't use dict.fromkeys because we would end up with many references
        # to the same list
        for variant in Component:
            self.alerts[variant] = []

    def process(self, records: Iterable[Record]) -> Sequence[Alert]:
        """
        Ingests an iterable of records, returning any Alerts.

        Args:
            records (Iterable[Record]): the records to process

        Returns:
            Sequence[Alert]: the emitted alerts, potentially empty
        """
        alerts = []
        for record in records:
            self.data.setdefault(record.satellite_id, []).append(record)
            alerts.extend(self.run_checks(record))

        return alerts

    def register_alert(self, component: Component) -> typing.Callable[[AlertCallback], AlertCallback]:
        """Register a function to check whether or not an Alert should be emitted."""
        def outer(f: typing.Callable[[Sequence[Record]], Alert | None]) -> AlertCallback:
            self.alerts[component].append(f)

            def wrapper(records: Sequence[Record]) -> Alert | None:
                return f(records)

            return wrapper

        return outer

    def run_checks(self, latest: Record) -> list[Alert]:
        """Run the registered callbacks."""
        alerts = []
        # only need to run checks on the satellite_id that was added though
        # this could change in the future depending on what we want to check
        for check in self.alerts[latest.component]:
            if t := check(self.data[latest.satellite_id]):
                alerts.append(t)

        return alerts
