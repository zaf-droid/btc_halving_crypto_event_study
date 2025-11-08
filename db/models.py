from sqlmodel import Field, SQLModel, Relationship
from typing import Annotated
from pydantic import EmailStr
import uuid
from schemas.user import  UserBase

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str = Field(max_length=100)

