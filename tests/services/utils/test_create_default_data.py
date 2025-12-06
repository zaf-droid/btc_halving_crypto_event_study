import pytest
from sqlmodel import SQLModel, Session, create_engine, select
from sqlmodel.pool import StaticPool
from services.utils.create_default_data import Events, insert_btc_halving_dates


@pytest.fixture
def engine():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    return engine


def test_insert_btc_halving_dates(engine):
    # First insertion
    insert_btc_halving_dates(engine)

    with Session(engine) as session:
        rows = session.exec(select(Events)).all()

    assert len(rows) == 4
    timestamps = sorted(r.timestamp for r in rows)
    assert timestamps == [
        1354060800,
        1468022400,
        1589155200,
        1713484800,
    ]


def test_insert_btc_halving_dates_is_idempotent(engine):
    # Run twice — should not duplicate entries
    insert_btc_halving_dates(engine)
    insert_btc_halving_dates(engine)

    with Session(engine) as session:
        rows = session.exec(select(Events)).all()

    assert len(rows) == 4  # still 4, no duplicates
