from cli.core.errors import wrap_mpt_api_error
from cli.core.mpt.models import Token
from mpt_api_client import MPTClient


# TODO: Remove or refactor verbose logging.
# This class currently does not handle verbose logs.
# Pending global logging refactor to add optional verbose support.
class MPTAccountService:
    """API service for managing api tokens operations."""

    def __init__(self, client: MPTClient):
        self.client = client

    @wrap_mpt_api_error
    def get_authentication(self, secret: str) -> Token:
        """Fetch an account authentication by secret token provided.

        Args:
            secret: The secret token string.

        Returns:
            An instance of the Token representing the fetched API authentication.
        """
        token_id = self._extract_token_id(secret)

        response_data = self.client.accounts.api_tokens.get(token_id).to_dict()
        return Token.model_validate(response_data)

    def _extract_token_id(self, secret):
        secret_split = secret.split(":")
        if len(secret_split) < 3:
            raise ValueError(f"Invalid token format: {secret}")

        return secret_split[1]
