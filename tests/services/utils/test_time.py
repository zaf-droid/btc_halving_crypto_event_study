from services.utils.time import granularity_to_interval, interval_to_granularity
import pytest

def test_granularity_to_interval():
    assert granularity_to_interval(30) == "30s"
    assert granularity_to_interval(120) == "2m"
    assert granularity_to_interval(3600) == "1h"
    assert granularity_to_interval(7200) == "2h"
    assert granularity_to_interval(86400) == "1d"
    assert granularity_to_interval(172800) == "2d"
    assert granularity_to_interval(75) == "75s"


def test_seconds():
    assert interval_to_granularity("1s") == 1
    assert interval_to_granularity("30s") == 30


def test_minutes():
    assert interval_to_granularity("1m") == 60
    assert interval_to_granularity("5m") == 300


def test_hours():
    assert interval_to_granularity("1h") == 3600
    assert interval_to_granularity("2h") == 7200


def test_days():
    assert interval_to_granularity("1d") == 86400
    assert interval_to_granularity("3d") == 259200


def test_empty_string_raises():
    with pytest.raises(ValueError):
        interval_to_granularity("")


def test_missing_number_raises():
    with pytest.raises(ValueError):
        interval_to_granularity("s")   # no numeric part


def test_non_numeric_raises():
    with pytest.raises(ValueError):
        interval_to_granularity("Xs")


def test_unknown_unit_raises():
    with pytest.raises(ValueError):
        interval_to_granularity("10w")
