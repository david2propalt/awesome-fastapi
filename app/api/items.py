from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.errors import ItemNotFoundError
from app.db.session import get_db
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemResponse

router = APIRouter(prefix="/items", tags=["items"])


def to_item_response(item: Item) -> ItemResponse:
    return ItemResponse(
        id=item.id,
        name=item.name,
        description=item.description,
        price=item.price,
    )


@router.post("/", response_model=ItemResponse, status_code=201)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)) -> ItemResponse:
    item = Item(
        name=payload.name,
        description=payload.description,
        price=payload.price,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return to_item_response(item)


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)) -> ItemResponse:
    item = db.get(Item, item_id)
    if item is None:
        raise ItemNotFoundError(item_id)
    return to_item_response(item)


@router.put("/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: int,
    payload: ItemCreate,
    db: Session = Depends(get_db),
) -> ItemResponse:
    item = db.get(Item, item_id)
    if item is None:
        raise ItemNotFoundError(item_id)

    item.name = payload.name
    item.description = payload.description
    item.price = payload.price

    db.add(item)
    db.commit()
    db.refresh(item)
    return to_item_response(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)) -> Response:
    item = db.get(Item, item_id)
    if item is None:
        raise ItemNotFoundError(item_id)

    db.delete(item)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
