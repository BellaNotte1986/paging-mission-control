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


checks: list[typing.Callable[[list[Record]], Alert | None]] = []


def register(f: typing.Callable[[list[Record]], Alert | None]):
    """Add a check to be run for each Record processed"""
    checks.append(f)
    return f


def parse_timestamp(s: str) -> dt.datetime:
    """Parse the timestamp from the record. For example, something like 20180101 23:01:05.001

    Args:
        s (str): the timestamp to be parsed

    Returns:
        dt.datetime: The parsed timestamp

    """

    # timestamp is annoyingly nonstandard
    return dt.datetime.strptime(s, "%Y%m%d %H:%M:%S.%f")


def read_records() -> typing.Iterable[Record]:
    input_file = sys.argv[1]  # first is filename
    with open(input_file) as f:
        for line in map(str.strip, f):
            (
                ts,
                sid,
                red_high,
                yellow_high,
                yellow_low,
                red_low,
                val,
                component,
            ) = line.split("|")
            yield Record(
                timestamp=parse_timestamp(ts),
                satellite_id=int(sid),
                red_high=int(red_high),
                yellow_high=int(yellow_high),
                yellow_low=int(yellow_low),
                red_low=int(red_low),
                val=float(val),
                component=Component(component),
            )


