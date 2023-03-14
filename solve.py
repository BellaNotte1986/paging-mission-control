import sys
from dataclasses import dataclass
import datetime as dt
import enum


class Component(enum.StrEnum):
    BATT = "BATT"
    TSTAT = "TSTAT"


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


def parse_timestamp(s: str) -> dt.datetime:
    """Parse the timestamp from the record. For example, something like 20180101 23:01:05.001

    Args:
        s (str): the timestamp to be parsed

    Returns:
        dt.datetime: The parsed timestamp

    """

    # timestamp is annoyingly nonstandard
    return dt.datetime.strptime(s, "%Y%m%d %H:%M:%S.%f")


if len(sys.argv) != 2:
    print(f"Usage: python mission_control.py [input_data]")
    sys.exit(1)
