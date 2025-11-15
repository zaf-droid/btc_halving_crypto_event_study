from sqlmodel import Session, select
from db.models import OHLC

def insert_ohlc_data(session: Session,
                     data_list: list[dict]):
    for item in data_list:

        row = OHLC(**item)

        exists = session.exec(
            select(OHLC).where(
                (OHLC.timestamp == row.timestamp) &
                (OHLC.base_currency == row.base_currency) &
                (OHLC.quote_currency == row.quote_currency) &
                (OHLC.interval == row.interval)
            )
        ).first()

        if not exists:
            session.add(row)

    session.commit()
