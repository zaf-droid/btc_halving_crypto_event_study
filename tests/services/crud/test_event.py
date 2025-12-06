from sqlmodel import SQLModel, create_engine
from sqlmodel.pool import StaticPool
from services.crud.event import *
import pytest

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_create_event_creates_and_returns_event(session):
    event_name = "SEC Meeting"
    event_description = "U.S. Securities and Exchange Commission meeting"
    timestamp = 1700000000
    params = EventParams(event_name=event_name,
                         description=event_description,
                         timestamp=timestamp)
    event = create_event(session, params)

    assert event.id is not None
    assert event.event_name == event_name
    assert event.description == event_description
    assert event.timestamp == timestamp

    result = session.exec(select(Events)).all()
    assert len(result) == 1


def test_get_event_data_basic(session, monkeypatch):
    # Mock granularity: say 1d = 100 time units to avoid real logic
    monkeypatch.setattr(
        "services.utils.time.interval_to_granularity",
        lambda unit: 100
    )

    items = [
        OHLC(timestamp=900, base_currency="BTC", quote_currency="USD",
             interval="1d", open=100, high=110, low=90, close=105, volume=5),

        OHLC(timestamp=1000, base_currency="BTC", quote_currency="USD",
             interval="1d", open=105, high=115, low=95, close=110, volume=6),

        OHLC(timestamp=1100, base_currency="BTC", quote_currency="USD",
             interval="1d", open=110, high=120, low=100, close=120, volume=7),
    ]
    session.add_all(items)
    session.commit()

    # event at timestamp=1000, window +/- 1 unit → timestamps 900..1100
    result = get_event_data(
        session=session,
        window_before_event=1,
        window_after_event=1,
        base_currency="BTC",
        quote_currency="USD",
        event_days_list=[1000],
        metric="close",
        window_unit="1d"
    )

    assert isinstance(result, list)
    assert len(result) == 1
    rows = result[0]
    assert len(rows) == 3

    # Check relative steps: [-1, 0, 1]
    assert [r["relative_event_steps"] for r in rows] == [-1, 0, 1]

    # Check daily returns
    # close: 105 → 110 → 120
    expected_returns = [
        0.0,
        (110-105)/105,
        (120-110)/110,
    ]
    for r, exp in zip(rows, expected_returns):
        assert abs(r["daily_return"] - exp) < 1e-9

    # cumulative_return monotonic increasing
    assert rows[0]["cumulative_return"] == 0
    assert rows[1]["cumulative_return"] > rows[0]["cumulative_return"]
    assert rows[2]["cumulative_return"] > rows[1]["cumulative_return"]
    assert rows[2]["cumulative_return"] == 120/105 - 1
