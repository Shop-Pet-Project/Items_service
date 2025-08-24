from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class ItemCreate(BaseModel):
    title: str = Field(min_length=1, max_length=32)
    price: float = Field(gt=0)


class ItemResponse(BaseModel):
    id: UUID
    title: str
    price: float

    model_config = ConfigDict(from_attributes=True)


class ItemsIdList(BaseModel):
    item_ids: list[UUID]

    model_config = ConfigDict(from_attributes=True)
