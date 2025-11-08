from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from typing import Annotated
import uuid


class UserBase(SQLModel):
    username: str = Field(max_length=50)
    email: Annotated[EmailStr, Field(max_length=30)]
    full_name: str

class UserIn(UserBase):
    password: str

class UserOut(UserBase):
    id: uuid.UUID