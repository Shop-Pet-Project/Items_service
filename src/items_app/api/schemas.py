import uuid
from pydantic import BaseModel, ConfigDict


class ItemCreate(BaseModel):
    title: str
    price: float


class ItemResponse(BaseModel):
    id: uuid.UUID
    title: str
    price: float

    model_config = ConfigDict(from_attributes=True)


class ItemsIdList(BaseModel):
    item_ids: list[uuid.UUID]

    model_config = ConfigDict(from_attributes=True)
