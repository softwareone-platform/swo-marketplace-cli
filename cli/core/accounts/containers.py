from cli.core.accounts.app import get_active_account
from cli.core.mpt.client import client_from_account
from dependency_injector import containers, providers


class AccountContainer(containers.DeclarativeContainer):
    """
    Container for account-related services and components.

    Attributes:
        account: Provides the active account.
        mpt_client: Provides the MPT client based on the active account.

    """

    account = providers.Singleton(get_active_account)
    mpt_client = providers.Singleton(client_from_account, account)
