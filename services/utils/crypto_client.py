import requests
from typing import Literal

def get_ohlc(base_url: str,
             start: int,
             end: int,
             limit: int = 1000,
             base_currency: Literal[ 'btc', 'eth', 'xrp' ] = 'btc',
             quote_currency: str | None = 'usd',
             granularity: int | None = 86400  # 1 day
             ):

    endpoint = f'ohlc/{base_currency}{quote_currency}/'
    params = {
        'step': granularity,
        'start': start,
        'end': end,
        'limit': limit,
    }
    response = requests.get(base_url + endpoint, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch OHLCV data:", response.status_code)
        return None