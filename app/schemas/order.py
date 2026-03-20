from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OrderCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_no: str = Field(..., min_length=1, max_length=64)
    user_id: int = Field(..., gt=0)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    total_amount: float = Field(..., gt=0)
    status: str = Field("pending", pattern="^(pending|paid|shipped|completed|cancelled)$")
    remark: str | None = Field(None, max_length=500)


class OrderResponse(BaseModel):
    model_config = ConfigDict(extra="ignore", from_attributes=True)

    id: int
    order_no: str
    user_id: int
    product_id: int
    quantity: int
    unit_price: float
    total_amount: float
    status: str
    remark: str | None
    paid_at: datetime | None
    shipped_at: datetime | None
    completed_at: datetime | None
    cancelled_at: datetime | None
    created_at: datetime
    updated_at: datetime
