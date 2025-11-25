from fastapi import APIRouter, Query, Depends, HTTPException
from sqlmodel import Session
from core.dependencies import get_session
from services.crud.ohlc import insert_ohlc_data
from classes.crypto_downloader import CryptoDownloader
from typing import Literal, Annotated
import time

downloader = CryptoDownloader()

router = APIRouter(prefix="/ohlc", tags=["ohlc"])

@router.post("/{base_currency}/{quote_currency}/fetch")
def fetch_and_store_ohlc(
    session: Annotated[Session, Depends(get_session)],
    base_currency: Literal["btc", "eth", "xrp"] = "btc",
    quote_currency: str = "usd",
    start: Annotated[int, Query(description="Start timestamp")] = None,
    end: Annotated[int, Query(description="End timestamp")] = None,
    granularity: Annotated[int, Query(description="Interval in seconds")] = 86400,
):
    end = end or int(time.time())
    data_list = downloader.get_historical_data(
        start=start,
        end=end,
        base_currency=base_currency,
        quote_currency=quote_currency,
        granularity=granularity
    )

    if not data_list:
        raise HTTPException(status_code=404, detail=f"No OHLCV data fetched. Quoted currency '{quote_currency}' may be incorrect.")

    # store in DB
    insert_ohlc_data(session, data_list)

    return {"ok": True, "fetched": len(data_list)}