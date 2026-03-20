import pytest
from fastapi.testclient import TestClient


class TestAuth:
    @pytest.fixture(autouse=True)
    def setup(self, client: TestClient) -> None:
        self.client = client
        self.client.post(
            "/users/",
            json={"username": "alice", "email": "alice@example.com", "password": "secret123"},
        )

    def test_login_success(self) -> None:
        response = self.client.post(
            "/auth/login", json={"username": "alice", "password": "secret123"}
        )

        assert response.status_code == 200
        payload = response.json()
        assert "access_token" in payload
        assert payload["token_type"] == "bearer"
        assert len(payload["access_token"]) > 0

    def test_login_wrong_password(self) -> None:
        response = self.client.post(
            "/auth/login", json={"username": "alice", "password": "wrongpass"}
        )

        assert response.status_code == 401
        payload = response.json()
        assert payload["success"] is False
        assert payload["error"]["code"] == 401

    def test_login_user_not_found(self) -> None:
        response = self.client.post(
            "/auth/login", json={"username": "ghost", "password": "secret123"}
        )

        assert response.status_code == 401
        payload = response.json()
        assert payload["success"] is False
        assert payload["error"]["code"] == 401

    def test_orders_require_auth(self) -> None:
        response = self.client.get("/orders/1")

        assert response.status_code == 401

    def test_orders_with_invalid_token(self) -> None:
        response = self.client.get(
            "/orders/1", headers={"Authorization": "Bearer invalid.token.here"}
        )

        assert response.status_code == 401
        payload = response.json()
        assert payload["success"] is False
        assert payload["error"]["code"] == 401

    def test_orders_with_valid_token(self) -> None:
        login_resp = self.client.post(
            "/auth/login", json={"username": "alice", "password": "secret123"}
        )
        token = login_resp.json()["access_token"]

        response = self.client.get("/orders/999", headers={"Authorization": f"Bearer {token}"})

        # 404 means auth passed, order just doesn't exist
        assert response.status_code == 404
