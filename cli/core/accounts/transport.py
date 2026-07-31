"""Transport settings backed by the accounts managed by the marketplace CLI.

These transport settings target the environment stored on a CLI account, so API clients
and scripts can reuse the CLI login without copying URLs. Use ``load_account`` to read
an account from the CLI accounts file, or ``CLIMPTClient`` for a fully wired client.
"""

from dataclasses import dataclass
from typing import override

from cli.core.accounts.models import Account
from mpt_api_client import TransportSettings

# Matches the default timeout previously applied by MPTClient.from_config.
API_REQUEST_TIMEOUT = 60.0


@dataclass
class CLITransport(TransportSettings):
    """Transport settings that target the environment of a CLI-stored account.

    The account is passed in resolved (see ``load_account``); these settings perform no
    file access of their own. When ``base_url`` is not provided explicitly, it is filled
    from the account's environment.

    Attributes:
        account: Account whose environment is used as the base URL.
    """

    timeout: float = API_REQUEST_TIMEOUT
    account: Account | None = None

    @override
    def __post_init__(self) -> None:
        """Resolve ``base_url`` from the account, then validate and normalize.

        Raises:
            ValueError: If neither ``base_url`` nor ``account`` is provided, or the
                resolved base URL is invalid.
        """
        if self.base_url is None and self.account is not None:
            self.base_url = self.account.environment
        super().__post_init__()
