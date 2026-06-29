from cli.core.accounts.models import Account
from mpt_api_client import MPTClient
from mpt_api_client.auth import BearerTokenAuthentication


def create_api_mpt_client_from_account(account: Account):
    """Create an API client MPTClient instance using credentials from the given account.

    Args:
        account: An Account object containing the base URL and API token.

    Returns:
        An instance of MPTClient to be used for API Client operations.
    """
    return MPTClient.from_config(
        authentication=BearerTokenAuthentication(account.token), base_url=account.environment
    )
