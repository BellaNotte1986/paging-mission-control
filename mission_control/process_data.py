from dataclasses import dataclass
import datetime as dt
import enum
import typing
from collections.abc import Iterable, Sequence
from functools import reduce
import json


class Component(enum.StrEnum):
    BATT = "BATT"
    TSTAT = "TSTAT"


class Alert(typing.TypedDict):
    satellite_id: int
    severity: str
    component: str
    timestamp: dt.datetime


@dataclass
class Record:
    timestamp: dt.datetime
    satellite_id: int
    red_high: int
    yellow_high: int
    yellow_low: int
    red_low: int
    val: float
    component: Component


class RecordProcessor:
    """Processes records and returns warnings if necessary"""

    def __init__(self):
        self.data: dict[int, list[Record]] = {}
        self.alerts: dict[
            Component, list[typing.Callable[[list[Record]], Alert | None]]
        ] = {}
        # can't use dict.fromkeys because we would end up with many references
        # to the same list
        for variant in Component:
            self.alerts[variant] = []

    def process(self, records: typing.Iterable[Record]) -> Sequence[Alert]:
        alerts = []
        for record in records:
            alerts.extend(self.run_checks(record))

        return alerts

    def register_alert(self, component: Component):
        """
        Register a function to check whether or not an Alert should be
        emitted
        """

        def outer(f: typing.Callable[[Sequence[Record]], Alert | None]):
            self.alerts[component].append(f)

            def wrapper(records: Sequence[Record]):
                return f(records)

            return wrapper

        return outer

    def run_checks(self, latest: Record) -> list[Alert]:
        self.data.setdefault(latest.satellite_id, []).append(latest)

        # first, remove data we don't need to keep anymore by constructing a new
        # dictionary.
        # in the future we could also do logging here

        # next, run alert checks
        alerts = []

        # only need to run checks on the satellite_id that was added though
        # this could change in the future depending on what we want to check
        for check in self.alerts[latest.component]:
            if t := check(self.data[latest.satellite_id]):
                alerts.append(t)

        return alerts
