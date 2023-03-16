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
        # if last element is a BATT, alert
        record = records[-1]
        if record.component != Component.BATT:
            return None

        return record.to_alert("RED LOW")

    # should produce an alert for every record with component == BATT
    out = rp.process(records)
    assert out == [
        record.to_alert("RED LOW")
        for record in records
        if record.component == Component.BATT
    ]


def test_filter_records_keep_all(rp: RecordProcessor, records: list[Record]) -> None:  # noqa: F811
    """Test checks are being run correctly."""
    # register 2 checks: one that always returns True, and one that always
    # returns False. We should see the input is equal to the output
    @rp.register_filter()
    def always_true(records: Sequence[Record]) -> list[bool]:
        return len(records) * [True]

    @rp.register_filter()
    def always_false(records: Sequence[Record]) -> list[bool]:
        return len(records) * [False]

    id1000_in = [x for x in records if x.satellite_id == 1000]
    id1001_in = [x for x in records if x.satellite_id == 1001]
    id1000_out = rp._filter_records(id1000_in)
    id1001_out = rp._filter_records(id1001_in)

    id1000_exp = [x for x in records if x.satellite_id == 1000]
    id1001_exp = [x for x in records if x.satellite_id == 1001]
    assert id1000_exp == id1000_out
    assert id1001_exp == id1001_out


def test_filter_records_remove_batt(rp: RecordProcessor, records: list[Record]) -> None:  # noqa: F811
    """Test checks filter properly."""
    @rp.register_filter()
    def batt(records: Sequence[Record]) -> list[bool]:
        return [record.component == Component.TSTAT for record in records]

    id1000_in = [x for x in records if x.satellite_id == 1000]
    id1001_in = [x for x in records if x.satellite_id == 1001]
    id1000_out = rp._filter_records(id1000_in)
    id1001_out = rp._filter_records(id1001_in)

    id1000_exp = [x for x in records if x.satellite_id == 1000 and x.component == Component.TSTAT]
    id1001_exp = [x for x in records if x.satellite_id == 1001 and x.component == Component.TSTAT]
    assert id1000_exp == id1000_out
    assert id1001_exp == id1001_out
