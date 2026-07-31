from dataclasses import dataclass
from typing import override

from cli.core.accounts.models import Account
from mpt_api_client import TransportSettings

API_REQUEST_TIMEOUT = 60.0


@dataclass
class CLITransport(TransportSettings):
    """Transport settings that target the environment of a CLI-stored account.

    Attributes:
        account: Account whose environment fills ``base_url`` when it is not passed.
    """

    timeout: float = API_REQUEST_TIMEOUT
    account: Account | None = None

    @override
    def __post_init__(self) -> None:
        """Resolve ``base_url`` from the account, then validate and normalize.

        Raises:
            ValueError: If no base URL can be resolved or it is invalid.
        """
        if self.base_url is None and self.account is not None:
            self.base_url = self.account.environment
        super().__post_init__()
