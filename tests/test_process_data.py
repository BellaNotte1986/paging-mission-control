from __future__ import annotations

import datetime as dt
from collections.abc import Sequence

import pytest

from paging_mission_control.process_data import Alert, Component, Record, RecordProcessor

from .test_main import records  # noqa: F401

UTC = dt.timezone(dt.timedelta(hours=0))


@pytest.fixture
def rp() -> RecordProcessor:
    """Record processor for sharing across tests."""
    return RecordProcessor()


def test_process(rp: RecordProcessor, records: list[Record]) -> None:  # noqa: F811
    """Test if records are processed correctly, i.e., the correct Alerts are returned."""
    @rp.register_alert(Component.BATT)
    def always_alert(records: Sequence[Record]) -> Alert | None:
        # first record with component BATT
        record = next(x for x in records if x.component == Component.BATT)
        return Alert(
            satelliteId=record.satellite_id,
            severity="RED LOW",
            component=Component.BATT,
            timestamp=record.timestamp,
        )

    out = rp.process(records[1:2])
    assert out == [
        Alert(
            satelliteId=1000,
            severity="RED LOW",
            component=Component.BATT,
            timestamp=dt.datetime(2018, 1, 1, 23, 1, 9, 521000, UTC),
        )
    ]


def test_run_checks_keep_all(rp: RecordProcessor, records: list[Record]) -> None:  # noqa: F811
    """Test checks are being run correctly."""
    # register 2 checks: one that always returns True, and one that always
    # returns False. We should see the input is equal to the output
    @rp.register_filter()
    def always_true(records: Sequence[Record]) -> list[bool]:
        return len(records) * [True]

    @rp.register_filter()
    def always_false(records: Sequence[Record]) -> list[bool]:
        return len(records) * [False]

    rp.process(records)

    id1000 = [x for x in records if x.satellite_id == 1000]
    id1001 = [x for x in records if x.satellite_id == 1001]
    assert id1000 == rp.data[1000]
    assert id1001 == rp.data[1001]
