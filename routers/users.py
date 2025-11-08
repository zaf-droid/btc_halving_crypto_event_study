from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Annotated
from sqlmodel import Session, select
from db.models import User
from core.dependencies import get_session
from schemas.query_parameters import QueryParams
from schemas.user import UserOut, UserIn
from services.crud.user import create_user, remove_user
import uuid


router = APIRouter(prefix="/users", tags=["users"])

@router.post("/add/", response_model=UserOut, status_code=201)
async def add_user(user: UserIn, session: Annotated[Session, Depends(get_session)]):
    user_in = create_user(session, user)
    user_out = UserOut(**user_in.model_dump())
    return user_out


@router.get("/getsome/", response_model=list[UserOut])
def read_users(session: Annotated[Session, Depends(get_session)],
                query_params: Annotated[QueryParams, Query()]):
    statement = select(User).offset(query_params.offset).limit(query_params.limit)
    users = session.exec(statement).all()
    return users


@router.get("/{User_id}", response_model=UserOut)
def read_user(user_id: uuid.UUID, session: Annotated[Session, Depends(get_session)]):
    user = session.get(User, user_id)
    if not User:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Code above omitted 👆

@router.delete("/{user_id}")
def delete_user(user_id: str, session: Annotated[Session, Depends(get_session)]):
    return remove_user(session, user_id)
