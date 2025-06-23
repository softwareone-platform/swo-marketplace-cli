from pydantic import BaseModel, Field


class Meta(BaseModel):
    limit: int
    offset: int
    total: int


type ListResponse[BaseModel] = tuple[Meta, list[BaseModel]]


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
    default: bool
    description: str
    display_order: int
    label: str
    name: str


class ItemGroup(BaseModel):
    id: str
    name: str


class Parameter(BaseModel):
    id: str
    name: str
    external_id: str = Field(alias="externalId")


class Item(BaseModel):
    id: str
    name: str


class Uom(BaseModel):
    id: str
    name: str


class Template(BaseModel):
    id: str
    name: str


class PriceList(BaseModel):
    id: str


class PriceListItem(BaseModel):
    id: str
    item: Item
