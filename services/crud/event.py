from sqlmodel import Session, select
from typing import Literal
from db.models import Events, OHLC
from schemas.query_parameters import EventParams
import polars as pl
from services.utils.time import interval_to_granularity


def create_event(session: Session, event_params: EventParams) -> Events:

    event = Events(**event_params.model_dump())
    session.add(event)
    session.commit()
    session.refresh(event)
    return event

def get_distinct_categories(session: Session):
    result = session.exec(select(Events.event_name).distinct())
    return [r for r in result]



def get_event_data(session: Session,
                   window_before_event: int,
                   window_after_event: int,
                   base_currency: str,
                   quote_currency: str,
                   event_days_list: list[int],
                   metric: Literal['open', 'high', 'low', 'close', 'volume'] = "close",
                   window_unit: Literal['1d', '12h', '6h', '1h', '15m', '5m', '1m', '30s', '10s', '5s', '1s'] = '1d'
                  ) -> list[dict]:
    timestamp_unit = interval_to_granularity(window_unit)
    json_list = []
    for event_date in event_days_list:

        data = session.exec(
            select(OHLC).where(
                (OHLC.base_currency == base_currency) &
                (OHLC.quote_currency == quote_currency) &
                (OHLC.interval == window_unit) &
                (OHLC.timestamp >= event_date - window_before_event * timestamp_unit) &
                (OHLC.timestamp <= event_date + window_after_event * timestamp_unit)
            )
        ).all()
        df = pl.DataFrame([d.model_dump() for d in data])

        df = df.with_columns(
            (pl.col(metric).pct_change().fill_null(0).alias("daily_return"))
        ).with_columns(
            ((pl.col("daily_return") + 1).cum_prod() - 1).alias("cumulative_return")
        )

        plot_start_window = -window_before_event
        plot_end_window = df.height + plot_start_window
        df = df.with_columns(
            (pl.arange(start=plot_start_window, end=plot_end_window).alias("relative_event_steps"))
        )

        json_list.append(df.filter(~pl.col('daily_return').is_null())
                         .select(pl.col('relative_event_steps', 'timestamp', 'base_currency', 'quote_currency', 'interval', metric, 'daily_return', 'cumulative_return'))
                         .to_dicts())
    return json_list
