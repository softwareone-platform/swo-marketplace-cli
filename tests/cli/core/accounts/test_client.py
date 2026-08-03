import pytest
from cli.core.accounts.client import CLIMPTClient
from cli.core.errors import CLIAccountError, NoActiveAccountFoundError
from mpt_api_client import TransportSettings
from mpt_api_client.auth import BearerTokenAuthentication


def test_binds_to_active_account(
    default_accounts_path, write_accounts, active_vendor_account, inactive_vendor_account
):
    write_accounts([inactive_vendor_account, active_vendor_account])

    result = CLIMPTClient()

    assert result.mpt_account == active_vendor_account


def test_targets_account_environment(default_accounts_path, write_accounts, active_vendor_account):
    write_accounts([active_vendor_account])

    result = CLIMPTClient()

    assert result.http_client.httpx_client.base_url == active_vendor_account.environment


def test_authenticates_with_account_token(
    default_accounts_path, write_accounts, authorization_header, active_vendor_account
):
    write_accounts([active_vendor_account])

    result = CLIMPTClient()

    assert (
        authorization_header(result.http_client.httpx_client.auth)
        == f"Bearer {active_vendor_account.token}"
    )


def test_explicit_account_skips_accounts_file(default_accounts_path, active_vendor_account):
    result = CLIMPTClient(account=active_vendor_account)

    assert (result.mpt_account, default_accounts_path.exists()) == (
        active_vendor_account,
        False,
    )


def test_injected_transport_is_used(active_vendor_account):
    transport = TransportSettings(base_url="https://api.elsewhere.com")

    result = CLIMPTClient(account=active_vendor_account, transport=transport)

    assert result.http_client.httpx_client.base_url == "https://api.elsewhere.com"


def test_injected_authentication_is_used(authorization_header, active_vendor_account):
    authentication = BearerTokenAuthentication("other-token")

    result = CLIMPTClient(account=active_vendor_account, authentication=authentication)

    assert authorization_header(result.http_client.httpx_client.auth) == "Bearer other-token"


def test_print_account_prints_bound_account(active_vendor_account, capsys):
    client = CLIMPTClient(account=active_vendor_account)

    client.print_account()  # act

    expected = f"Current active account: {active_vendor_account.id} ({active_vendor_account.name})"
    assert expected in capsys.readouterr().out


def test_file_missing_raises_error(default_accounts_path):
    with pytest.raises(CLIAccountError, match="not found"):
        CLIMPTClient()


def test_no_active_account_raises_error(
    default_accounts_path, write_accounts, inactive_vendor_account
):
    write_accounts([inactive_vendor_account])

    with pytest.raises(NoActiveAccountFoundError):
        CLIMPTClient()
