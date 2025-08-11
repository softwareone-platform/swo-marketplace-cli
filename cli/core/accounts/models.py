from pydantic import BaseModel


class Account(BaseModel):
    """Model representing a user account."""

    id: str
    name: str
    type: str
    token: str
    token_id: str
    environment: str
    is_active: bool = False

    def is_operations(self) -> bool:
        """Check if the account type is 'Operations'.

        Returns:
            True if the account type is 'Operations', False otherwise.

        """
        return self.type == "Operations"
