from cli.core.mpt.models.accounts import Account
from pydantic import BaseModel, Field


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
