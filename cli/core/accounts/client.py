"""MPT client backed by the accounts managed by the marketplace CLI.

The CLI stores its accounts in ``~/.swocli/accounts.json``. This client authenticates
with the stored bearer token and targets the stored environment of the active account
(or of an explicitly passed account), so API clients and scripts can reuse the CLI login
without copying tokens or URLs.
"""

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

    By default the active account (``is_active: true``) from ``~/.swocli/accounts.json``
    is used; pass ``account`` to use a specific account instead. The bound account is
    exposed as ``mpt_account``:

        >>> client = CLIMPTClient()

    Custom ``transport`` and ``authentication`` can be injected; whichever is omitted is
    built from the account (``CLITransport`` / ``CLIAuthenticator``).
    """

    def __init__(
        self,
        account: Account | None = None,
        transport: TransportSettings | None = None,
        authentication: Authentication | None = None,
    ) -> None:
        """Resolve the account and initialize the client bound to it.

        Args:
            account: Account to bind the client to. When omitted, the active account is
                loaded from the CLI accounts file; pass it explicitly to avoid any file
                access, even when ``transport`` and ``authentication`` are injected.
            transport: Transport settings to use. Defaults to ``CLITransport`` targeting
                the account's environment.
            authentication: Authentication to use. Defaults to ``CLIAuthenticator`` with
                the account's token.

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
