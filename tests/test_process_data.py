from __future__ import annotations

import datetime as dt
from collections.abc import Sequence

import pytest

from paging_mission_control.process_data import Alert, Component, Record, RecordProcessor

UTC = dt.timezone(dt.timedelta(hours=0))


@pytest.fixture
def rp() -> RecordProcessor:
    """Record processor for sharing across tests."""
    t = RecordProcessor()

    @t.register_alert(Component.BATT)
    def always_alert(records: Sequence[Record]) -> Alert | None:
        # first record with component BATT
        record = next(x for x in records if x.component == Component.BATT)
        return Alert(
            satelliteId=record.satellite_id,
            severity="RED LOW",
            component=Component.BATT,
            timestamp=record.timestamp,
        )

    return t


@pytest.fixture
def input_data() -> list[Record]:
    """Input data fixture."""
    return [Record(dt.datetime(2018, 1, 1, 23, 1, 5, 1000, UTC), 1000, 17, 15, 9, 8, 7.8, Component.BATT)]


def test_process(rp: RecordProcessor, input_data: list[Record]) -> None:
    """Test if records are processed correctly, i.e., the correct Alerts are returned."""
    out = rp.process(input_data)
    assert out == [
        Alert(
            satelliteId=1000,
            severity="RED LOW",
            component=Component.BATT,
            timestamp=dt.datetime(2018, 1, 1, 23, 1, 5, 1000, UTC),
        )
    ]
