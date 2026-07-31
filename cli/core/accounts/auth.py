"""Authentication provider backed by the accounts managed by the marketplace CLI.

The provider authenticates with the bearer token stored on a CLI account, so API clients
and scripts can reuse the CLI login without copying tokens. Use ``load_account`` to read
an account from the CLI accounts file, or ``CLIMPTClient`` for a fully wired client.
"""

from cli.core.accounts.models import Account
from mpt_api_client.auth import BearerTokenAuthentication


class CLIAuthenticator(BearerTokenAuthentication):
    """Authenticate with the bearer token of an account stored by the marketplace CLI.

    The account is passed in resolved (see ``load_account``); this provider performs no
    file access of its own:

        >>> authentication = CLIAuthenticator(load_account())
    """

    def __init__(self, account: Account) -> None:
        """Initialize the bearer token from the account.

        Args:
            account: Account whose token authenticates the requests.
        """
        super().__init__(account.token)
