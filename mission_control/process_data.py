import sys
from dataclasses import dataclass
import datetime as dt
import enum
import typing


class Component(enum.StrEnum):
    BATT = "BATT"
    TSTAT = "TSTAT"


class Alert(typing.TypedDict):
    satelliteId: int
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


checks: dict[str, typing.Callable[[list[Record]], Alert | None]] = {}


def register(name: str):
    """Add a check to be run for each Record processed"""

    def outer(f: typing.Callable[[list[Record]], Alert | None]):
        checks[name] = f

        def wrapper(records: list[Record]):
            return f(records)

        return wrapper

    return outer


def run_checks(records: list[Record]) -> list[Alert]:
    alerts = []
    for name, check in checks.items():
        if alert := check(records):
            alerts.append(alert)
    return alerts
