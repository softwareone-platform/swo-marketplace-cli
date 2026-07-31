from operator import attrgetter

from cli.core.accounts.client import CLIMPTClient
from dependency_injector import containers, providers


class AccountContainer(containers.DeclarativeContainer):
    """
    Container for account-related services and components.

    Attributes:
        api_mpt_client: Provides the API MPT client bound to the active account.
        account: Provides the account the API MPT client is bound to.

    """

    api_mpt_client = providers.Singleton(CLIMPTClient)
    account = providers.Callable(attrgetter("mpt_account"), api_mpt_client)
