from sqlmodel import Field, SQLModel, Relationship
import uuid
from schemas.user import  UserBase
from schemas.query_parameters import EventParams

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str = Field(max_length=100)

class OHLC(SQLModel, table=True):
    base_currency: str = Field(max_length=15, primary_key=True)
    quote_currency: str = Field(max_length=15, primary_key=True)
    timestamp: int = Field(ge=0, primary_key=True)
    interval: str = Field(max_length=10, primary_key=True)
    open: float
    high: float
    low: float
    close: float
    volume: float

class Events(EventParams, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
