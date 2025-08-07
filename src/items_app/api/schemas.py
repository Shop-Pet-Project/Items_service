from pydantic import BaseModel, ConfigDict
from items_app.infrastructure.models import Item


class ItemCreate(BaseModel):
    title: str
    price: float


class ItemResponse(BaseModel):
    id: int
    title: str
    price: float

    model_config = ConfigDict(from_attributes=True)