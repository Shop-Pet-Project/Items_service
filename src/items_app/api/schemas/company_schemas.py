from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


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
