from fastapi import HTTPException


class UnauthorizedError(HTTPException):
    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(
            status_code=401,
            detail=message,
            headers={"WWW-Authenticate": "Bearer"},
        )


class UserNotFoundError(HTTPException):
    def __init__(self, user_id: int) -> None:
        super().__init__(status_code=404, detail=f"User {user_id} not found")


class ProductNotFoundError(HTTPException):
    def __init__(self, product_id: int) -> None:
        super().__init__(status_code=404, detail=f"Product {product_id} not found")


class OrderNotFoundError(HTTPException):
    def __init__(self, order_id: int) -> None:
        super().__init__(status_code=404, detail=f"Order {order_id} not found")
