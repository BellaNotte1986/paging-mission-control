from __future__ import annotations

import datetime as dt
import enum
import typing
from collections.abc import Iterable, Sequence
from dataclasses import dataclass


class Component(str, enum.Enum):
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

    def to_alert(self, severity: str) -> Alert:
        """Helper function to create an Alert."""
        return Alert(
            satelliteId=self.satellite_id,
            severity=severity,
            component=self.component,
            timestamp=self.timestamp,
        )


AlertCallback = typing.Callable[["Sequence[Record]"], typing.Optional[Alert]]
FilterCallback = typing.Callable[["Sequence[Record]"], "Iterable[bool]"]


class RecordProcessor:
    """Processes records and returns warnings if necessary."""

    def __init__(self):
        self.data: dict[int, list[Record]] = {}
        self.filters: list[FilterCallback] = []
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
            alerts.extend(self._run_checks(self.data[record.satellite_id]))

        return alerts

    def register_alert(self, component: Component) -> typing.Callable[[AlertCallback], AlertCallback]:
        """Register a function to check whether or not an Alert should be emitted."""
        def outer(f: AlertCallback) -> AlertCallback:
            self.alerts[component].append(f)

            def wrapper(records: Sequence[Record]) -> Alert | None:
                return f(records)

            return wrapper

        return outer

    def register_filter(self) -> typing.Callable[[FilterCallback], FilterCallback]:
        """
        Register a function to check if a record should be kept.

        The most recently added record will be the last element.
        """
        def outer(f: FilterCallback) -> FilterCallback:
            self.filters.append(f)

            def wrapper(records: Sequence[Record]) -> Iterable[bool]:
                return f(records)

            return wrapper

        return outer

    def _run_checks(self, satellite: list[Record]) -> Iterable[Alert]:
        """Run the registered callbacks."""
        # remove records that we don't need to store anymore
        # in order for a record to be removed, all filters must return False
        # could also parallelize in the future
        if self.filters:
            new_records = []
            for record, filter_results in zip(satellite, zip(*(f(satellite) for f in self.filters))):
                if any(filter_results):
                    new_records.append(record)

            self.data[satellite[-1].satellite_id] = new_records

        alerts = []
        # only need to run checks on the satellite_id that was just added,
        # though this could change in the future depending on what we want to
        # check
        for check in self.alerts[satellite[-1].component]:
            if t := check(self.data[satellite[-1].satellite_id]):
                alerts.append(t)

        return alerts
