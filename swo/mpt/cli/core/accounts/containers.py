from dependency_injector import containers, providers
from swo.mpt.cli.core.accounts.app import get_active_account
from swo.mpt.cli.core.mpt.client import client_from_account


class AccountContainer(containers.DeclarativeContainer):
    """
    Container for account-related services and components.

    Attributes:
        account: Provides the active account.
        mpt_client: Provides the MPT client based on the active account.

    """

    account = providers.Singleton(get_active_account)
    mpt_client = providers.Singleton(client_from_account, account)
