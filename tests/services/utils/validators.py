import pytest
from sqlmodel import SQLModel, Field, create_engine, Session, select
from fastapi import HTTPException
from db.models import OHLC
from services.utils.validators import validate_value_in_db, validate_pairs_in_db




@pytest.fixture
def session():
    engine = create_engine("sqlite://", echo=False)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture
def populated_db(session):
    """Insert sample rows."""
    rows = [
        OHLC(base_currency="btc", quote_currency="usd", timestamp=1732387200, interval='1d', open=100000.0,
             high=1200000.0, low=100000.0, close=1200000.0, volume=12000000000.0),
        OHLC(base_currency="btc", quote_currency="eur",timestamp=1732387200, interval='1d', open=100000.0,
             high=1200000.0, low=100000.0, close=1200000.0, volume=12000000000.0),
        OHLC(base_currency="eth", quote_currency="usd",timestamp=1732387200, interval='1d', open=1000.0,
             high=12000.0, low=1000.0, close=12000.0, volume=120000.0),
    ]
    for row in rows:
        session.add(row)
    session.commit()
    return session


def test_validate_value_exists(session):
    base_currency = 'btc'
    item = OHLC(base_currency=base_currency,
    quote_currency='usd',
    timestamp=1732387200,
    interval='1d',
    open=100000.0,
    high=1200000.0,
    low=100000.0,
    close=1200000.0,
    volume=12000000000.0)

    session.add(item)
    session.commit()

    # Act & Assert: should NOT raise
    validate_value_in_db(
        session=session,
        model=OHLC,
        column=OHLC.base_currency,
        value=base_currency,
    )


def test_validate_value_not_exists(session):

    base_currency = 'eth'
    with pytest.raises(HTTPException) as exc:
        validate_value_in_db(
            session=session,
            model=OHLC,
            column=OHLC.base_currency,
            value=base_currency,
        )

    assert exc.value.status_code == 400
    assert base_currency in exc.value.detail


def test_validate_pairs_success(populated_db):
    validate_pairs_in_db(
        populated_db,
        OHLC,
        {
            OHLC.base_currency: "btc",
            OHLC.quote_currency: "usd",
        }
    )
    # If no exception is raised, the test passes.


def test_validate_pairs_failure(populated_db):
    with pytest.raises(HTTPException) as exc:
        validate_pairs_in_db(
            populated_db,
            OHLC,
            {
                OHLC.base_currency: "btc",
                OHLC.quote_currency: "usd",
                OHLC.interval: '1m' # does NOT exist
            }
        )

    assert exc.value.status_code == 400
    assert "btc" in exc.value.detail
    assert "usd" in exc.value.detail
    assert "1m" in exc.value.detail


def test_validate_pairs_full_row_mismatch(populated_db):

    with pytest.raises(HTTPException):
        validate_pairs_in_db(
            populated_db,
            OHLC,
            {
                OHLC.base_currency: "eth",
                OHLC.quote_currency: "eur",  # both exist but never together
            }
        )
