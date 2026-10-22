import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

engine = create_engine(
    "sqlite://",  # in-memory database
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def test_shorten_and_redirect(client):
    r = client.post("/shorten", json={"target_url": "https://example.com/very/long/path"})
    assert r.status_code == 201
    code = r.json()["short_code"]
    assert len(code) == 7

    r = client.get(f"/{code}", follow_redirects=False)
    assert r.status_code == 307
    assert r.headers["location"] == "https://example.com/very/long/path"


def test_clicks_are_counted(client):
    code = client.post("/shorten", json={"target_url": "https://example.com"}).json()["short_code"]
    client.get(f"/{code}", follow_redirects=False)
    client.get(f"/{code}", follow_redirects=False)
    assert client.get(f"/stats/{code}").json()["clicks"] == 2


def test_custom_code_and_conflict(client):
    r = client.post("/shorten", json={"target_url": "https://example.com", "custom_code": "my-link"})
    assert r.status_code == 201
    assert r.json()["short_url"].endswith("/my-link")
    r = client.post("/shorten", json={"target_url": "https://other.com", "custom_code": "my-link"})
    assert r.status_code == 409


def test_invalid_url_rejected(client):
    r = client.post("/shorten", json={"target_url": "not a url"})
    assert r.status_code == 422


def test_delete(client):
    code = client.post("/shorten", json={"target_url": "https://example.com"}).json()["short_code"]
    assert client.delete(f"/{code}").status_code == 204
    assert client.get(f"/{code}", follow_redirects=False).status_code == 404