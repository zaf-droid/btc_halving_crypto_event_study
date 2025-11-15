from services.utils.time import granularity_to_interval

def test_granularity_to_interval():
    assert granularity_to_interval(30) == "30s"
    assert granularity_to_interval(120) == "2m"
    assert granularity_to_interval(3600) == "1h"
    assert granularity_to_interval(7200) == "2h"
    assert granularity_to_interval(86400) == "1d"
    assert granularity_to_interval(172800) == "2d"
    assert granularity_to_interval(75) == "75s"