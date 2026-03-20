import pytest
from fastapi.testclient import TestClient


class TestUsers:
    @pytest.fixture(autouse=True)
    def setup(self, client: TestClient) -> None:
        self.client = client

    def test_create_user(self) -> None:
        response = self.client.post(
            "/users/",
            json={"username": "alice", "email": "alice@example.com", "password": "secret123"},
        )

        assert response.status_code == 201
        payload = response.json()
        assert isinstance(payload["id"], int)
        assert payload["username"] == "alice"
        assert payload["email"] == "alice@example.com"
        assert "password" not in payload
        assert "created_at" in payload
        assert "updated_at" in payload

    def test_get_user_by_id(self) -> None:
        created = self.client.post(
            "/users/",
            json={"username": "bob", "email": "bob@example.com", "password": "secret123"},
        )
        user_id = created.json()["id"]

        response = self.client.get(f"/users/{user_id}")

        assert response.status_code == 200
        assert response.json()["username"] == "bob"

    def test_get_user_not_found(self) -> None:
        response = self.client.get("/users/999")

        assert response.status_code == 404
        payload = response.json()
        assert payload["success"] is False
        assert payload["error"]["code"] == 404

    def test_update_user(self) -> None:
        created = self.client.post(
            "/users/",
            json={"username": "carol", "email": "carol@example.com", "password": "secret123"},
        )
        user_id = created.json()["id"]

        response = self.client.put(
            f"/users/{user_id}",
            json={
                "username": "carol_updated",
                "email": "carol_new@example.com",
                "password": "newpass123",
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["id"] == user_id
        assert payload["username"] == "carol_updated"
        assert payload["email"] == "carol_new@example.com"
        assert "password" not in payload

    def test_update_user_not_found(self) -> None:
        response = self.client.put(
            "/users/999",
            json={"username": "ghost", "email": "ghost@example.com", "password": "secret123"},
        )

        assert response.status_code == 404
        payload = response.json()
        assert payload["success"] is False
        assert payload["error"]["code"] == 404

    def test_delete_user(self) -> None:
        created = self.client.post(
            "/users/",
            json={"username": "dave", "email": "dave@example.com", "password": "secret123"},
        )
        user_id = created.json()["id"]

        delete_response = self.client.delete(f"/users/{user_id}")
        assert delete_response.status_code == 204
        assert delete_response.text == ""

        get_response = self.client.get(f"/users/{user_id}")
        assert get_response.status_code == 404

    def test_delete_user_not_found(self) -> None:
        response = self.client.delete("/users/999")

        assert response.status_code == 404
        payload = response.json()
        assert payload["success"] is False
        assert payload["error"]["code"] == 404

    def test_delete_user_is_soft_delete(self) -> None:
        created = self.client.post(
            "/users/",
            json={"username": "eve", "email": "eve@example.com", "password": "secret123"},
        )
        user_id = created.json()["id"]

        self.client.delete(f"/users/{user_id}")

        response = self.client.delete(f"/users/{user_id}")
        assert response.status_code == 404
