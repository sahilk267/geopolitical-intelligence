import pytest
from datetime import datetime, timedelta
from types import SimpleNamespace

from app.core.scheduler import _compute_next_run, _should_run, _croniter_available


def test_compute_next_run_interval():
    schedule = SimpleNamespace(interval_minutes=15, cron_expression=None)
    reference = datetime(2026, 3, 28, 10, 0)

    next_run = _compute_next_run(schedule, reference)

    assert next_run == reference + timedelta(minutes=15)


@pytest.mark.skipif(not _croniter_available, reason="croniter is not installed")
def test_compute_next_run_cron():
    schedule = SimpleNamespace(interval_minutes=None, cron_expression="0 12 * * *")
    reference = datetime(2026, 3, 28, 9, 45)

    next_run = _compute_next_run(schedule, reference)

    assert next_run is not None
    assert next_run.hour == 12
    assert next_run.minute == 0
    assert next_run.date() == reference.date()


def test_should_run_when_no_last_run_at():
    schedule = SimpleNamespace(interval_minutes=30, cron_expression=None, last_run_at=None)
    now = datetime(2026, 3, 28, 10, 0)

    assert _should_run(schedule, now) is True


def test_should_run_interval_due():
    schedule = SimpleNamespace(interval_minutes=20, cron_expression=None, last_run_at=datetime(2026, 3, 28, 9, 35))
    now = datetime(2026, 3, 28, 9, 55)

    assert _should_run(schedule, now) is True


def test_should_run_interval_not_due():
    schedule = SimpleNamespace(interval_minutes=20, cron_expression=None, last_run_at=datetime(2026, 3, 28, 9, 45))
    now = datetime(2026, 3, 28, 9, 55)

    assert _should_run(schedule, now) is False


@pytest.mark.skipif(not _croniter_available, reason="croniter is not installed")
def test_should_run_cron_expression():
    schedule = SimpleNamespace(interval_minutes=None, cron_expression="0 12 * * *", last_run_at=datetime(2026, 3, 28, 11, 0), name="cron-test")
    now = datetime(2026, 3, 28, 12, 0)

    assert _should_run(schedule, now) is True
