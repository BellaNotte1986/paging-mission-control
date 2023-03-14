import datetime as dt
from pathlib import Path

import pytest

from mission_control import __main__
from mission_control.process_data import Component, Record

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

TIMESTAMPS = [
    dt.datetime(2018, 1, 1, 23, 1, 5, 1000, dt.UTC),
    dt.datetime(2018, 1, 1, 23, 1, 9, 521000, dt.UTC),
    dt.datetime(2018, 1, 1, 23, 1, 26, 11000, dt.UTC),
    dt.datetime(2018, 1, 1, 23, 1, 38, 1000, dt.UTC),
    dt.datetime(2018, 1, 1, 23, 1, 49, 21000, dt.UTC),
    dt.datetime(2018, 1, 1, 23, 2, 9, 14000, dt.UTC),
    dt.datetime(2018, 1, 1, 23, 2, 10, 21000, dt.UTC),
    dt.datetime(2018, 1, 1, 23, 2, 11, 302000, dt.UTC),
    dt.datetime(2018, 1, 1, 23, 3, 3, 8000, dt.UTC),
    dt.datetime(2018, 1, 1, 23, 3, 5, 9000, dt.UTC),
    dt.datetime(2018, 1, 1, 23, 4, 6, 17000, dt.UTC),
    dt.datetime(2018, 1, 1, 23, 4, 11, 531000, dt.UTC),
    dt.datetime(2018, 1, 1, 23, 5, 5, 21000, dt.UTC),
    dt.datetime(2018, 1, 1, 23, 5, 7, 421000, dt.UTC),
]


@pytest.fixture
def test_data() -> list[tuple[int, int, int, int, int, float, Component]]:
    """Test fixture for sample input."""
    return [
        (1001, 101, 98, 25, 20, 99.9, Component("TSTAT")),
        (1000, 17, 15, 9, 8, 7.8, Component("BATT")),
    ]


@pytest.fixture
def records(test_data: list[tuple[int, int, int, int, int, float, Component]]) -> list[Record]:
    """Test fixture for parsed sample input."""
    return [Record(ts, *x) for ts, x in zip(TIMESTAMPS, test_data)]


@pytest.mark.parametrize(
    "inp,expected", list((s.split("|", 1)[0], ans) for s, ans in zip(TEST_INPUT.split("\n"), TIMESTAMPS))
)
def test_parse_timestamp(inp: str, expected: dt.datetime) -> None:
    """Test parsing the timestamps."""
    assert __main__.parse_timestamp(inp) == expected


def test_read_records(tmp_path: Path, records: list[Record]) -> None:
    """Test parsing the records."""
    f = tmp_path / "test_data.txt"
    f.write_text("\n".join(TEST_INPUT.split("\n")[:2]))

    assert list(__main__.read_records(f)) == records
