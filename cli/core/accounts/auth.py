from cli.core.accounts.models import Account
from mpt_api_client.auth import BearerTokenAuthentication


class CLIAuthenticator(BearerTokenAuthentication):
    """Authenticate with the bearer token of a CLI-stored account."""

    def __init__(self, account: Account) -> None:
        """Initialize the bearer token from the account.

        Args:
            account: Account whose token authenticates the requests.
        """
        super().__init__(account.token)
