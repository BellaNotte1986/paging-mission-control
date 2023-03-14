import sys
from dataclasses import dataclass
import datetime as dt
import enum
from operator import attrgetter
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


class Filter(typing.Protocol):
    def keep( self, record: Record) -> bool:
        """Determine whether or not if this record is notable."""
        ...

    def check(self, records: list[Record]) -> Alert | None:
        """Return a warning if one should be emitted, None otherwise"""
        ...


def parse_timestamp(s: str) -> dt.datetime:
    """Parse the timestamp from the record. For example, something like 20180101 23:01:05.001

    Args:
        s (str): the timestamp to be parsed

    Returns:
        dt.datetime: The parsed timestamp

    """

    # timestamp is annoyingly nonstandard
    return dt.datetime.strptime(s, "%Y%m%d %H:%M:%S.%f")


def read_records() -> list[Record]:
    input_file = sys.argv[1]  # first is filename
    records = []
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
            records.append(
                Record(
                    timestamp=parse_timestamp(ts),
                    satellite_id=int(sid),
                    red_high=int(red_high),
                    yellow_high=int(yellow_high),
                    yellow_low=int(yellow_low),
                    red_low=int(red_low),
                    val=float(val),
                    component=Component(component),
                )
            )

    # not sure if sorting is necessary. the test data is ordered, but it could
    # be possible that data may arrive out of order. if it's ordered anyways,
    # we don't pay that much since timsort can handle it relatively quickly
    return sorted(records, key=attrgetter("timestamp"))


if len(sys.argv) != 2:
    print(f"Usage: python mission_control.py [input_data]")
    sys.exit(1)

records = read_records()
print(*records, sep="\n")
