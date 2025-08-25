from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

""" Схемы для валидации данных, связанных с товарами. """
class ItemCreate(BaseModel):
    title: str = Field(min_length=1, max_length=32)
    price: float = Field(gt=0)
    company_id: UUID


class ItemResponse(BaseModel):
    id: UUID
    title: str
    price: float
    company_id: UUID

    model_config = ConfigDict(from_attributes=True)


class ItemsIdList(BaseModel):
    item_ids: list[UUID]

    model_config = ConfigDict(from_attributes=True)


""" Схемы для валидации данных, связанных с компаниями. """
class CompanyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)


class CompanyResponse(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class CompanyUpdate(BaseModel):
    id: UUID
    name: str = Field(min_length=1, max_length=64)


class CompanyUpdateResponse(BaseModel):
    message: Optional[str] = "Company updated successfully"
    company: CompanyResponse
