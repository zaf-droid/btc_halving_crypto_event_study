from typing import Literal
from services.utils import crypto_client, time as time_utils
import time
import polars as pl

class CryptoDownloader:
    _base_url = 'https://www.bitstamp.net/api/v2/'

    _start_date = 1274496000

    def __init__(self, exchange: str = 'bitstamp') -> None:
        self.exchange = exchange

    def get_historical_data(self,
                            start: None | int = None,
                            end: None | int = None,
                            base_currency: Literal[ 'btc', 'eth', 'xrp' ] = 'btc',
                            quote_currency: str | None = 'usd',
                            granularity: int | None = 86400  # 1 day
                            ) -> list[dict]:
        if end is None:
            end = int(time.time())
        if start is None:
            start = self._start_date
        df_list = []
        step = granularity * 999
        time_interval = time_utils.granularity_to_interval(granularity)
        for start_date in range(start, end, step):
            end_date = start_date + step
            btc_ohlcv = crypto_client.get_ohlc(base_url=self._base_url,
                                               base_currency=base_currency,
                                               quote_currency=quote_currency,
                                               granularity=granularity,
                                               start=start_date,
                                               end=min(end_date, end)
                                               )

            if btc_ohlcv is not None:
                data = btc_ohlcv['data']['ohlc']
                df = pl.DataFrame(data)
                df_list.append(df)

            else:
                print("No OHLCV data fetched.")
        if not df_list:
            return []
        else:
            final_df = pl.concat(df_list).with_columns(pl.lit(base_currency).alias('base_currency'),
                                                       pl.lit(quote_currency).alias('quote_currency'),
                                                       pl.lit(time_interval).alias('interval'))

            final_df = final_df.unique(subset=['base_currency', 'quote_currency', 'timestamp', 'interval'])

            return final_df.to_dicts()
