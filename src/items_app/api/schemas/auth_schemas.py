from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class UserCreateSchema(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    email: EmailStr
    password: str = Field(min_length=8)


class UserResponseSchema(BaseModel):
    id: UUID
    username: str
    email: EmailStr
