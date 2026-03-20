import pytest
from fastapi.testclient import TestClient

PRODUCT_PAYLOAD = {"name": "Widget", "price": 9.99, "stock": 100}


class TestProducts:
    @pytest.fixture(autouse=True)
    def setup(self, client: TestClient) -> None:
        self.client = client

    def test_create_product(self) -> None:
        response = self.client.post("/products/", json=PRODUCT_PAYLOAD)

        assert response.status_code == 201
        payload = response.json()
        assert isinstance(payload["id"], int)
        assert payload["name"] == "Widget"
        assert payload["price"] == 9.99
        assert payload["stock"] == 100
        assert "created_at" in payload
        assert "updated_at" in payload

    def test_get_product_by_id(self) -> None:
        created = self.client.post("/products/", json=PRODUCT_PAYLOAD)
        product_id = created.json()["id"]

        response = self.client.get(f"/products/{product_id}")

        assert response.status_code == 200
        payload = response.json()
        assert payload["name"] == "Widget"
        assert payload["price"] == 9.99

    def test_get_product_not_found(self) -> None:
        response = self.client.get("/products/999")

        assert response.status_code == 404
        payload = response.json()
        assert payload["success"] is False
        assert payload["error"]["code"] == 404

    def test_update_product(self) -> None:
        created = self.client.post("/products/", json=PRODUCT_PAYLOAD)
        product_id = created.json()["id"]

        response = self.client.put(
            f"/products/{product_id}",
            json={"name": "Updated Widget", "price": 19.99, "stock": 50},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["id"] == product_id
        assert payload["name"] == "Updated Widget"
        assert payload["price"] == 19.99
        assert payload["stock"] == 50

    def test_update_product_not_found(self) -> None:
        response = self.client.put("/products/999", json={"name": "X", "price": 1.0, "stock": 0})

        assert response.status_code == 404
        payload = response.json()
        assert payload["success"] is False
        assert payload["error"]["code"] == 404

    def test_delete_product(self) -> None:
        created = self.client.post("/products/", json=PRODUCT_PAYLOAD)
        product_id = created.json()["id"]

        delete_response = self.client.delete(f"/products/{product_id}")
        assert delete_response.status_code == 204
        assert delete_response.text == ""

        get_response = self.client.get(f"/products/{product_id}")
        assert get_response.status_code == 404

    def test_delete_product_not_found(self) -> None:
        response = self.client.delete("/products/999")

        assert response.status_code == 404
        payload = response.json()
        assert payload["success"] is False
        assert payload["error"]["code"] == 404
