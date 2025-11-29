from pydantic import BaseModel
from typing import Annotated, Optional, Literal
from fastapi import Query
from sqlmodel import SQLModel, Field

class QueryParams(BaseModel):
    offset: Annotated[int, Query(ge=0)] = 0
    limit: Annotated[int, Query(le=100)] = 100

class EventParams(SQLModel):
    event_name: str = Field(max_length=50, index=True)
    description: str
    timestamp: int = Field(max_length=50)

class EventStudyParams(BaseModel):
    window_before_event: Optional[int] = 30
    window_after_event: Optional[int] = 30
    window_unit: Literal['1d', '12h', '6h', '1h', '15m', '5m', '1m', '30s', '10s', '5s', '1s'] = '1d'
    metric: Optional[Literal['open', 'high', 'low', 'close', 'volume']] = "close"
    base_currency: Optional[str] = "btc"
    quote_currency: Optional[str] = "usd"
    event_name: Optional[str] = "BTC Halving"
