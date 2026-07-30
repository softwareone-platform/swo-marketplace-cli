from cli.core.accounts.models import Account
from mpt_api_client import MPTClient, TransportSettings
from mpt_api_client.auth import BearerTokenAuthentication
from mpt_api_client.http import HTTPClient

# Matches the default timeout previously applied by MPTClient.from_config.
API_REQUEST_TIMEOUT = 60.0


def create_api_mpt_client(token: str, environment: str) -> MPTClient:
    """Create an API client MPTClient instance for the given token and environment.

    Args:
        token: SoftwareOne Marketplace API token.
        environment: Protocol and host part of the API URL.

    Returns:
        An instance of MPTClient to be used for API Client operations.
    """
    return MPTClient(
        HTTPClient(
            TransportSettings(base_url=environment, timeout=API_REQUEST_TIMEOUT),
            authentication=BearerTokenAuthentication(token),
        )
    )


def create_api_mpt_client_from_account(account: Account):
    """Create an API client MPTClient instance using credentials from the given account.

    Args:
        account: An Account object containing the base URL and API token.

    Returns:
        An instance of MPTClient to be used for API Client operations.
    """
    return create_api_mpt_client(account.token, account.environment)
