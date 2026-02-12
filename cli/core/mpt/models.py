from pydantic import BaseModel, Field


class Meta(BaseModel):
    """Model representing pagination metadata."""

    limit: int
    offset: int
    total: int


type ListResponse[BaseModel] = tuple[Meta, list[BaseModel]]


class Account(BaseModel):
    """Model representing an MPT account."""

    id: str
    name: str
    type: str


class Token(BaseModel):
    """Model representing an authentication token."""

    id: str
    account: Account
    token: str


class Product(BaseModel):
    """Model representing a product."""

    id: str
    name: str
    status: str
    vendor: Account


class ParameterGroup(BaseModel):
    """Model representing a parameter group."""

    id: str
    default: bool
    description: str | None = None
    display_order: int = Field(alias="displayOrder")
    label: str
    name: str


class ItemGroup(BaseModel):
    """Model representing an item group."""

    id: str
    name: str


class Parameter(BaseModel):
    """Model representing a parameter."""

    id: str
    external_id: str | None = Field(default=None, alias="externalId")
    name: str


class MPTItem(BaseModel):
    """Model representing an item."""

    id: str
    name: str


class Uom(BaseModel):
    """Model representing a unit of measure."""

    id: str
    name: str


class Template(BaseModel):
    """Model representing a template."""

    id: str
    name: str


class PriceList(BaseModel):
    """Model representing a price list."""

    id: str


class PriceListItem(BaseModel):
    """Model representing a price list item."""

    id: str
    catalog_item: MPTItem = Field(alias="item")
