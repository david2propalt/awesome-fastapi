from pydantic import BaseModel, ConfigDict, Field


class ItemCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    price: float = Field(..., gt=0)


class ItemResponse(BaseModel):
    model_config = ConfigDict(extra="ignore", from_attributes=True)

    id: int
    name: str
    description: str | None = None
    price: float
