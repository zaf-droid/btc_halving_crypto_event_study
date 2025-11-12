import pytest
from sqlmodel import SQLModel, Session, create_engine, select
from fastapi import HTTPException
from db.models import User
from schemas.user import UserIn
from services.crud.user import create_user, remove_user
from core.security import verify_password
from uuid import uuid4

@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

def test_create_user(session: Session):
    user_in = UserIn(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        password="securepass"
    )

    user = create_user(session, user_in)

    # Basic assertions
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert verify_password("securepass",user.hashed_password)

    # Check persistence in DB
    statement = select(User).where(User.username == "testuser")
    db_user = session.exec(statement).first()
    assert db_user is not None
    assert db_user.email == "test@example.com"


@pytest.fixture
def setup_remove_user(session):
    u = User(
        username="john",
        email="john@example.com",
        full_name="John Doe",
        hashed_password="fakehash"
    )
    session.add(u)
    session.commit()
    session.refresh(u)
    return u


def test_remove_user_success(session, setup_remove_user):
    user = setup_remove_user
    result = remove_user(session, str(user.id))
    assert result == {"ok": True}

    # Ensure user is deleted
    assert session.get(User, user.id) is None


def test_remove_user_invalid_uuid(session):

    with pytest.raises(HTTPException) as exc_info:
        remove_user(session, "not-a-uuid")

    assert exc_info.value.status_code == 400
    assert "Invalid UUID" in exc_info.value.detail


def test_remove_user_not_found(session):
    fake_id = str(uuid4())

    with pytest.raises(HTTPException) as exc_info:
        remove_user(session, fake_id)

    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail
