import sys
import typing
import datetime as dt
from .process_data import Alert, Component, Record, register


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


if len(sys.argv) != 2:
    print(f"Usage: python mission_control.py [input_data]")
    sys.exit(1)


@register(name="LOW VOLTAGE")
def low_voltage(records: list[Record]) -> Alert | None:
    print("low voltage check")

