from cli.core.mpt.models.products import MPTItem
from pydantic import BaseModel, Field


class PriceList(BaseModel):
    """Model representing a price list."""

    id: str


class PriceListItem(BaseModel):
    """Model representing a price list item."""

    id: str
    catalog_item: MPTItem = Field(alias="item")
