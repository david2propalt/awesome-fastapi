import pytest
from fastapi.testclient import TestClient

ORDER_PAYLOAD = {
    "order_no": "ORD-20260320-0001",
    "user_id": 1,
    "product_id": 1,
    "quantity": 2,
    "unit_price": 9.99,
    "total_amount": 19.98,
    "status": "pending",
    "remark": None,
}


class TestOrders:
    @pytest.fixture(autouse=True)
    def setup(self, client: TestClient) -> None:
        self.client = client
        self.client.post(
            "/users/",
            json={"username": "testuser", "email": "testuser@example.com", "password": "secret123"},
        )
        resp = self.client.post(
            "/auth/login", json={"username": "testuser", "password": "secret123"}
        )
        self.auth_headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

    def test_create_order(self) -> None:
        response = self.client.post("/orders/", json=ORDER_PAYLOAD, headers=self.auth_headers)

        assert response.status_code == 201
        payload = response.json()
        assert isinstance(payload["id"], int)
        assert payload["order_no"] == "ORD-20260320-0001"
        assert payload["user_id"] == 1
        assert payload["product_id"] == 1
        assert payload["quantity"] == 2
        assert payload["unit_price"] == 9.99
        assert payload["total_amount"] == 19.98
        assert payload["status"] == "pending"
        assert payload["remark"] is None
        assert payload["paid_at"] is None
        assert payload["shipped_at"] is None
        assert payload["completed_at"] is None
        assert payload["cancelled_at"] is None
        assert "created_at" in payload
        assert "updated_at" in payload

    def test_create_order_unauthorized(self) -> None:
        response = self.client.post("/orders/", json=ORDER_PAYLOAD)

        assert response.status_code == 401

    def test_get_order_by_id(self) -> None:
        created = self.client.post("/orders/", json=ORDER_PAYLOAD, headers=self.auth_headers)
        order_id = created.json()["id"]

        response = self.client.get(f"/orders/{order_id}", headers=self.auth_headers)

        assert response.status_code == 200
        payload = response.json()
        assert payload["order_no"] == "ORD-20260320-0001"
        assert payload["user_id"] == 1

    def test_get_order_not_found(self) -> None:
        response = self.client.get("/orders/999", headers=self.auth_headers)

        assert response.status_code == 404
        payload = response.json()
        assert payload["success"] is False
        assert payload["error"]["code"] == 404

    def test_update_order(self) -> None:
        created = self.client.post("/orders/", json=ORDER_PAYLOAD, headers=self.auth_headers)
        order_id = created.json()["id"]

        updated_payload = {**ORDER_PAYLOAD, "status": "paid", "quantity": 3, "total_amount": 29.97}
        response = self.client.put(
            f"/orders/{order_id}", json=updated_payload, headers=self.auth_headers
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["id"] == order_id
        assert payload["status"] == "paid"
        assert payload["quantity"] == 3
        assert payload["total_amount"] == 29.97

    def test_update_order_not_found(self) -> None:
        response = self.client.put("/orders/999", json=ORDER_PAYLOAD, headers=self.auth_headers)

        assert response.status_code == 404
        payload = response.json()
        assert payload["success"] is False
        assert payload["error"]["code"] == 404

    def test_delete_order(self) -> None:
        created = self.client.post("/orders/", json=ORDER_PAYLOAD, headers=self.auth_headers)
        order_id = created.json()["id"]

        delete_response = self.client.delete(f"/orders/{order_id}", headers=self.auth_headers)
        assert delete_response.status_code == 204
        assert delete_response.text == ""

        get_response = self.client.get(f"/orders/{order_id}", headers=self.auth_headers)
        assert get_response.status_code == 404

    def test_delete_order_not_found(self) -> None:
        response = self.client.delete("/orders/999", headers=self.auth_headers)

        assert response.status_code == 404
        payload = response.json()
        assert payload["success"] is False
        assert payload["error"]["code"] == 404
