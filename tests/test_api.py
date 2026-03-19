import os
from typing import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import Base, get_db
from app.main import app

DEFAULT_TEST_DATABASE_URL = (
    "mysql+pymysql://app_test:app_test@127.0.0.1:3306/awesome_fastapi_test"
)
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", DEFAULT_TEST_DATABASE_URL)

test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db() -> Generator[Session, None, None]:
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_function() -> None:
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)


def test_health_check() -> None:
    response = client.get("/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["message"] == "Service is healthy"


def test_create_item() -> None:
    response = client.post(
        "/items/",
        json={
            "name": "Keyboard",
            "description": "Mechanical",
            "price": 99.9,
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["id"] == 1
    assert payload["name"] == "Keyboard"


def test_get_item_by_id() -> None:
    created = client.post(
        "/items/",
        json={"name": "Mouse", "description": "Wireless", "price": 59.0},
    )
    item_id = created.json()["id"]

    response = client.get(f"/items/{item_id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "Mouse"


def test_get_item_not_found() -> None:
    response = client.get("/items/999")

    assert response.status_code == 404
    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == 404


def test_update_item() -> None:
    created = client.post(
        "/items/",
        json={"name": "Monitor", "description": "24-inch", "price": 199.0},
    )
    item_id = created.json()["id"]

    response = client.put(
        f"/items/{item_id}",
        json={"name": "Monitor Pro", "description": "27-inch", "price": 299.0},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == item_id
    assert payload["name"] == "Monitor Pro"
    assert payload["description"] == "27-inch"
    assert payload["price"] == 299.0


def test_update_item_not_found() -> None:
    response = client.put(
        "/items/999",
        json={"name": "Unknown", "description": "N/A", "price": 1.0},
    )

    assert response.status_code == 404
    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == 404


def test_delete_item() -> None:
    created = client.post(
        "/items/",
        json={"name": "Desk", "description": "Wood", "price": 120.0},
    )
    item_id = created.json()["id"]

    delete_response = client.delete(f"/items/{item_id}")
    assert delete_response.status_code == 204
    assert delete_response.text == ""

    get_response = client.get(f"/items/{item_id}")
    assert get_response.status_code == 404


def test_delete_item_not_found() -> None:
    response = client.delete("/items/999")

    assert response.status_code == 404
    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == 404
