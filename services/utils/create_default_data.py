from db.models import Events
from sqlmodel import Session, select

def insert_btc_halving_dates(engine):
    event_name = 'BTC Halving'
    description = 'dates when Bitcoin halving events occurred'

    defaults = [
            Events(event_name=event_name, description=description, timestamp=1354060800),
            Events(event_name=event_name, description=description, timestamp=1468022400),
            Events(event_name=event_name, description=description, timestamp=1589155200),
            Events(event_name=event_name, description=description, timestamp=1713484800),
        ]


    with Session(engine) as session:
        for row in defaults:
            exists = session.exec(
                select(Events).where(Events.timestamp == row.timestamp)
            ).first()

            if not exists:
                session.add(row)

        session.commit()
