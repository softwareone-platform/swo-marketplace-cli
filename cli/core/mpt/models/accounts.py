from pydantic import BaseModel


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
