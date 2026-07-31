from cli.core.accounts.auth import CLIAuthenticator


def test_account_token_sets_bearer_header(authorization_header, active_vendor_account):
    authenticator = CLIAuthenticator(active_vendor_account)

    result = authorization_header(authenticator)

    assert result == f"Bearer {active_vendor_account.token}"
