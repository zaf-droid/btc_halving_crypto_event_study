from sqlmodel import Session
from db.models import User
from schemas.user import UserIn
from core.security import hash_password
from uuid import UUID
from fastapi import HTTPException


def create_user(session: Session, user_in: UserIn) -> User:
    user = User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hash_password(user_in.password)
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def remove_user(session: Session, user_id: str) -> dict[str, bool]:
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    user = session.get(User, user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}
