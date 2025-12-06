import pytest
from db.database import create_engine
from db.models import Events, OHLC
from core.dependencies import get_session
from fastapi.testclient import TestClient
from main import app
from sqlmodel import Session, SQLModel
from sqlmodel import StaticPool
from typing import List


def make_fake_ohlc(
    base="BTC",
    quote="USD",
    interval="1d",
    start_timestamp=1499754000,
    count=10,
    step=86400,
) -> List[OHLC]:

    rows = []
    for i in range(count):
        ts = start_timestamp + i * step

        price = 100 + i * 5  # nice increasing pattern

        rows.append(
            OHLC(
                base_currency=base,
                quote_currency=quote,
                timestamp=ts,
                interval=interval,
                open=price,
                high=price + 2,
                low=price - 2,
                close=price + 1,
                volume=10 + i,
            )
        )
    return rows

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def fake_ohlc_data(session):
    rows = make_fake_ohlc()

    with session:
        session.add_all(rows)
        session.commit()

    return rows


def test_create_event_study(client):
    payload = {
        "event_name": "SEC Meeting",
        "description": "SEC Meeting description",
        "timestamp": 1700000000
    }

    response = client.post("event-study/new", json=payload)

    assert response.status_code == 201
    data = response.json()

    assert data["event_name"] == "SEC Meeting"
    assert data["description"] == "SEC Meeting description"
    assert data["timestamp"] == 1700000000




def test_get_event_study_results(client, session, fake_ohlc_data):
    window_before_event = 1
    window_after_event = 2
    # Insert one event so validation passes
    with session as s:
        s.add(Events(event_name="BTC Halving", description="test", timestamp=1499926000))
        s.commit()


    params = {
        "event_name": "BTC Halving",
        "base_currency": "BTC",
        "quote_currency": "USD",
        "window_unit": "1d",
        "window_before_event": window_before_event,
        "window_after_event": window_after_event,
        "metric": "close",
    }

    response = client.get("event-study/data", params=params)
    assert response.status_code == 200
    assert len(response.json()[0]) == (window_before_event + window_after_event)
