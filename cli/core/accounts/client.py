from cli.core.accounts.auth import CLIAuthenticator
from cli.core.accounts.loader import load_account
from cli.core.accounts.models import Account
from cli.core.accounts.transport import CLITransport
from cli.core.console import console
from mpt_api_client import MPTClient, TransportSettings
from mpt_api_client.auth import Authentication
from mpt_api_client.http import HTTPClient


class CLIMPTClient(MPTClient):
    """MPT client bound to an account stored by the marketplace CLI.

    Defaults to the active account from ``~/.swocli/accounts.json``; the bound account
    is exposed as ``mpt_account``:

        >>> client = CLIMPTClient()
    """

    def __init__(
        self,
        account: Account | None = None,
        transport: TransportSettings | None = None,
        authentication: Authentication | None = None,
    ) -> None:
        """Resolve the account and initialize the client bound to it.

        Args:
            account: Account to bind to. Defaults to the active account from the CLI
                accounts file.
            transport: Transport settings. Defaults to ``CLITransport`` for the account.
            authentication: Authentication. Defaults to ``CLIAuthenticator`` for the
                account.

        Raises:
            CLIAccountError: If the accounts file is missing or invalid.
            NoActiveAccountFoundError: If no account is active.
        """
        if account is None:
            account = load_account()
        super().__init__(
            HTTPClient(
                transport or CLITransport(account=account),
                authentication=authentication or CLIAuthenticator(account),
            )
        )
        self.mpt_account = account

    def print_account(self) -> None:
        """Print the account this client is bound to."""
        account_label = self.mpt_account.label
        console.print(f"Current active account: {account_label}")
