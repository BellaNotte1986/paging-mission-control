import datetime as dt
import json
import sys
import typing
from collections.abc import Sequence

from .process_data import Alert, Component, Record, RecordProcessor


class AlertEncoder(json.JSONEncoder):
    """
    Allows serialization of datetime.datetime instances.

    Should only be used for serializing `Alert`s
    """

    def default(self, o: dt.datetime) -> str:
        """Serializes datetimes in ISO 8601 format."""
        # this technically doesn't match the sample output, since Python's
        # datetime doesn't use the "Z" for UTC, but it's the same so it should
        # be fine
        return o.isoformat()


def parse_timestamp(s: str) -> dt.datetime:
    """
    Parse the timestamp from the record timestamp format.

    Args:
        s (str): the timestamp to be parsed

    Returns:
        dt.datetime: The parsed timestamp

    """
    # not sure what time zone to use, but the sample output uses UTC, so that
    # will probably be fine
    ts = dt.datetime.strptime(s, "%Y%m%d %H:%M:%S.%f")
    return ts.replace(tzinfo=dt.UTC)


def read_records() -> typing.Iterable[Record]:
    """Read the records from the filename passed as command line argument."""
    input_file = sys.argv[1]  # first is the path of the program itself
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


rp = RecordProcessor()


@rp.register_alert(component=Component.BATT)
def low_voltage(records: Sequence[Record]) -> Alert | None:
    """Check if there are 3 or more records with a voltage reading below the red_low in the last 5 minutes."""
    if not records:
        return None

    notable = []
    last = records[-1]
    for record in records:
        if (
            record.val < record.red_low
            and (last.timestamp - record.timestamp).seconds < 5 * 60
        ):
            notable.append(record)

    if len(notable) > 2:
        return Alert(
            satelliteId=notable[0].satellite_id,
            severity="RED LOW",
            component=notable[0].component,
            timestamp=notable[0].timestamp,
        )


@rp.register_alert(component=Component.TSTAT)
def high_temp(records: Sequence[Record]) -> Alert | None:
    """Check if there are 3 or more records with a temperature reading above the red_high in the last 5 minutes."""
    if not records:
        return None
    notable = []
    last = records[-1]
    for record in records:
        if (
            record.val > record.red_high
            and (last.timestamp - record.timestamp).seconds < 5 * 60
        ):
            notable.append(record)

    if len(notable) > 2:
        return Alert(
            satelliteId=notable[0].satellite_id,
            severity="RED HIGH",
            component=notable[0].component,
            timestamp=notable[0].timestamp,
        )


if len(sys.argv) != 2:
    print("Usage: python -m mission_control [input_data_file]")
    sys.exit(1)

alerts = rp.process(read_records())
print(json.dumps(alerts, cls=AlertEncoder, indent=4))
