import httpx
from cli.core.accounts.auth import CLIAuthenticator


def authorization_header(authenticator):
    request = httpx.Request("GET", "https://example.com/public/v1/")
    return next(authenticator.auth_flow(request)).headers["Authorization"]


def test_account_token_sets_bearer_header(active_vendor_account):
    authenticator = CLIAuthenticator(active_vendor_account)

    result = authorization_header(authenticator)

    assert result == f"Bearer {active_vendor_account.token}"
