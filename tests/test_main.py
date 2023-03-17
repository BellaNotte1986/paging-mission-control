from __future__ import annotations

import datetime as dt
from pathlib import Path

import pytest

from paging_mission_control import __main__
from paging_mission_control.process_data import Component, Record

TEST_INPUT = """\
20180101 23:01:05.001|1001|101|98|25|20|99.9|TSTAT
20180101 23:01:09.521|1000|17|15|9|8|7.8|BATT
20180101 23:01:26.011|1001|101|98|25|20|99.8|TSTAT
20180101 23:01:38.001|1000|101|98|25|20|102.9|TSTAT
20180101 23:01:49.021|1000|101|98|25|20|87.9|TSTAT
20180101 23:02:09.014|1001|101|98|25|20|89.3|TSTAT
20180101 23:02:10.021|1001|101|98|25|20|89.4|TSTAT
20180101 23:02:11.302|1000|17|15|9|8|7.7|BATT
20180101 23:03:03.008|1000|101|98|25|20|102.7|TSTAT
20180101 23:03:05.009|1000|101|98|25|20|101.2|TSTAT
20180101 23:04:06.017|1001|101|98|25|20|89.9|TSTAT
20180101 23:04:11.531|1000|17|15|9|8|7.9|BATT
20180101 23:05:05.021|1001|101|98|25|20|89.9|TSTAT
20180101 23:05:07.421|1001|17|15|9|8|7.9|BATT"""

UTC = dt.timezone(dt.timedelta(hours=0))

TIMESTAMPS = [
    dt.datetime(2018, 1, 1, 23, 1, 5, 1000, UTC),
    dt.datetime(2018, 1, 1, 23, 1, 9, 521000, UTC),
    dt.datetime(2018, 1, 1, 23, 1, 26, 11000, UTC),
    dt.datetime(2018, 1, 1, 23, 1, 38, 1000, UTC),
    dt.datetime(2018, 1, 1, 23, 1, 49, 21000, UTC),
    dt.datetime(2018, 1, 1, 23, 2, 9, 14000, UTC),
    dt.datetime(2018, 1, 1, 23, 2, 10, 21000, UTC),
    dt.datetime(2018, 1, 1, 23, 2, 11, 302000, UTC),
    dt.datetime(2018, 1, 1, 23, 3, 3, 8000, UTC),
    dt.datetime(2018, 1, 1, 23, 3, 5, 9000, UTC),
    dt.datetime(2018, 1, 1, 23, 4, 6, 17000, UTC),
    dt.datetime(2018, 1, 1, 23, 4, 11, 531000, UTC),
    dt.datetime(2018, 1, 1, 23, 5, 5, 21000, UTC),
    dt.datetime(2018, 1, 1, 23, 5, 7, 421000, UTC),
]


@pytest.fixture
def records() -> list[Record]:
    """Test fixture for parsed sample input."""
    data = [
        (1001, 101, 98, 25, 20, 99.9, Component.TSTAT),
        (1000, 17, 15, 9, 8, 7.8, Component.BATT),
        (1001, 101, 98, 25, 20, 99.8, Component.TSTAT),
        (1000, 101, 98, 25, 20, 102.9, Component.TSTAT),
        (1000, 101, 98, 25, 20, 87.9, Component.TSTAT),
        (1001, 101, 98, 25, 20, 89.3, Component.TSTAT),
        (1001, 101, 98, 25, 20, 89.4, Component.TSTAT),
        (1000, 17, 15, 9, 8, 7.7, Component.BATT),
        (1000, 101, 98, 25, 20, 102.7, Component.TSTAT),
        (1000, 101, 98, 25, 20, 101.2, Component.TSTAT),
        (1001, 101, 98, 25, 20, 89.9, Component.TSTAT),
        (1000, 17, 15, 9, 8, 7.9, Component.BATT),
        (1001, 101, 98, 25, 20, 89.9, Component.TSTAT),
        (1001, 17, 15, 9, 8, 7.9, Component.BATT),
    ]

    return [Record(ts, *x) for ts, x in zip(TIMESTAMPS, data)]


@pytest.mark.parametrize(
    "inp,expected", list((s.split("|", 1)[0], ans) for s, ans in zip(TEST_INPUT.split("\n"), TIMESTAMPS))
)
def test_parse_timestamp(inp: str, expected: dt.datetime) -> None:
    """Test parsing the timestamps."""
    assert __main__.parse_timestamp(inp) == expected


def test_read_records(tmp_path: Path, records: list[Record]) -> None:
    """Test parsing the records."""
    f = tmp_path / "test_data.txt"
    f.write_text(TEST_INPUT)

    assert list(__main__.read_records(f)) == records


def test_age(records: list[Record]) -> None:
    """Test age filter."""
    records = (
        [Record(dt.datetime(2018, 1, 1, 22, tzinfo=UTC), 1000, 20, 20, 20, 20, 20, Component.BATT)] + records
    )
    # all entries are within 5 minutes of each other, except the one we just added
    assert list(__main__.age(records)) == [False] + [True] * (len(records) - 1)


def test_high_temp(records: list[Record]) -> None:
    """Test high temp alert."""
    assert (
        __main__.high_temp([x for x in records if x.satellite_id == 1000])
        == records[3].to_alert("RED HIGH")
    )


def test_low_voltage(records: list[Record]) -> None:
    """Test low voltage alert."""
    assert (
        __main__.low_voltage([x for x in records if x.satellite_id == 1000])
        == records[1].to_alert("RED LOW")
    )


def test_high_temp_emit_multiple(records: list[Record]) -> None:
    """High temp alert should emit multiple, different alerts when 4 records greater than limit are entered."""
    # insert a new record, identical to the third record, so that another alert is emitted
    r = Record(dt.datetime(2018, 1, 1, 23, 1, 39, 1000, UTC), 1000, 101, 98, 25, 20, 102.9, Component.TSTAT)
    records.insert(4, r)
    assert (
        __main__.high_temp([x for x in records if x.satellite_id == 1000])
        == records[4].to_alert("RED HIGH")
    )
