from typing import TYPE_CHECKING, Self

from pydantic import BaseModel

if TYPE_CHECKING:
    from cli.core.mpt.models import Token


class Account(BaseModel):
    """Model representing a user account."""

    id: str
    name: str
    type: str
    token: str
    token_id: str
    environment: str
    is_active: bool = False

    @property
    def label(self) -> str:
        """Human-readable identifier, e.g. ``ACC-1234 (My Account)``."""
        return f"{self.id} ({self.name})"

    def is_operations(self) -> bool:
        """Check if the account type is 'Operations'."""
        return self.type == "Operations"

    @classmethod
    def from_token(cls, token: "Token", environment: str) -> Self:
        """Create an account from an MPT token."""
        return cls(
            id=token.account.id,
            name=token.account.name,
            type=token.account.type,
            token=token.token,
            token_id=token.id,
            environment=environment,
            is_active=True,
        )

    @classmethod
    def from_secret(cls, secret: str, environment: str) -> Self:
        """Create a provisional account for authenticating a raw secret during login."""
        return cls(
            id="",
            name="",
            type="",
            token=secret,
            token_id="",
            environment=environment,
        )
