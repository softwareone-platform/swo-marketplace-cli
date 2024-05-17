from typing import Annotated, TypeAlias, TypeVar

from pydantic import BaseModel, Field


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
    token: str


class Product(BaseModel):
    id: str
    name: str
    status: str
    vendor: Account


class ParameterGroup(BaseModel):
    id: str
    name: str


class ItemGroup(BaseModel):
    id: str
    name: str


class Parameter(BaseModel):
    id: str
    name: str
    external_id: Annotated[str, Field(alias="externalId")]


class Item(BaseModel):
    id: str
    name: str


class Uom(BaseModel):
    id: str
    name: str


class Template(BaseModel):
    id: str
    name: str


class Pricelist(BaseModel):
    id: str


class PricelistItem(BaseModel):
    id: str
    item: Item
