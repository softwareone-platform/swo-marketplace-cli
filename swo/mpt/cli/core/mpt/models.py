from typing import TypeAlias, TypeVar

from pydantic import BaseModel


class Meta(BaseModel):
    limit: int
    offset: int
    total: int


T = TypeVar("T", bound=BaseModel)
ListResponse: TypeAlias = tuple[Meta, list[T]]


class Account(BaseModel):
    id: str
    name: str
    type: str


class Token(BaseModel):
    id: str
    account: Account


class Product(BaseModel):
    id: str
    name: str
    status: str
    vendor: Account
