from pydantic import BaseModel


class Meta(BaseModel):
    """Model representing pagination metadata."""

    limit: int
    offset: int
    total: int


type ListResponse[MPTModel] = tuple[Meta, list[MPTModel]]
