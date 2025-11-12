import pytest
from main import app
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool
from fastapi.testclient import TestClient
from core.dependencies import get_session

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_add_user(session: Session):
    def get_session_override():
        return session
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)

    payload = {
        "username": "john",
        "email": "john@example.com",
        "full_name": "John Doe",
        "password": "secret123"
    }
    response = client.post("/users/add/", json=payload)
    app.dependency_overrides.clear()
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "john"
    assert "id" in data
    assert data["email"] == "john@example.com"


def test_read_users(session: Session):
    def get_session_override():
        return session
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    client.post("/users/add/", json={
        "username": "alice",
        "email": "alice@example.com",
        "full_name": "Alice Doe",
        "password": "secret"
    })
    client.post("/users/add/", json={"username": "john",
                                     "email": "john@example.com",
                                     "full_name": "John Doe",
                                     "password": "secret123"})

    response = client.get("/users/getsome/?offset=0&limit=10")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "username" in data[0]
    assert "id" in data[0]
    assert data[0]["username"] == "alice"
    assert data[0]["email"] == "alice@example.com"
    assert data[0]["full_name"] == "Alice Doe"


def test_read_user_by_id(session: Session):
    def get_session_override():
        return session
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)

    post_resp = client.post("/users/add/", json={
        "username": "mike",
        "email": "mike@example.com",
        "full_name": "Mike Doe",
        "password": "secret"
    })
    user_id = post_resp.json()["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == "mike"


def test_delete_user(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    post_resp = client.post("/users/add/", json={
        "username": "bob",
        "email": "bob@example.com",
        "full_name": "Bob Doe",
        "password": "secret"
    })

    user_id = post_resp.json()["id"]

    delete_resp = client.delete(f"/users/{user_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json() == {"ok": True}
    get_resp = client.get(f"/users/{user_id}")
    print(get_resp)
    assert get_resp.status_code == 404
    app.dependency_overrides.clear()


def test_delete_user_invalid_uuid(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    response = client.delete("/users/not-a-uuid")
    app.dependency_overrides.clear()
    assert response.status_code == 400