from pydantic import BaseModel
from typing import Annotated
from fastapi import Query

class QueryParams(BaseModel):
    offset: Annotated[int, Query(ge=0)] = 0
    limit: Annotated[int, Query(le=100)] = 100