from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.errors import OrderNotFoundError
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.order import Order
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse

router = APIRouter(prefix="/orders", tags=["orders"])


def to_order_response(order: Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        order_no=order.order_no,
        user_id=order.user_id,
        product_id=order.product_id,
        quantity=order.quantity,
        unit_price=order.unit_price,
        total_amount=order.total_amount,
        status=order.status,
        remark=order.remark,
        paid_at=order.paid_at,
        shipped_at=order.shipped_at,
        completed_at=order.completed_at,
        cancelled_at=order.cancelled_at,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> OrderResponse:
    order = Order(**payload.model_dump())
    db.add(order)
    db.commit()
    db.refresh(order)
    return to_order_response(order)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> OrderResponse:
    order = db.get(Order, order_id)
    if order is None:
        raise OrderNotFoundError(order_id)
    return to_order_response(order)


@router.put("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    payload: OrderCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> OrderResponse:
    order = db.get(Order, order_id)
    if order is None:
        raise OrderNotFoundError(order_id)
    for key, value in payload.model_dump().items():
        setattr(order, key, value)
    db.commit()
    db.refresh(order)
    return to_order_response(order)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Response:
    order = db.get(Order, order_id)
    if order is None:
        raise OrderNotFoundError(order_id)
    db.delete(order)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
