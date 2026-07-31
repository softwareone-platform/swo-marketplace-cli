import json

import httpx
import pytest
from cli.core.accounts.client import CLIMPTClient
from cli.core.accounts.handlers import JsonFileHandler
from cli.core.errors import CLIAccountError, NoActiveAccountFoundError


@pytest.fixture
def default_accounts_path(mocker, account_file_path):
    mocker.patch.object(JsonFileHandler, "_default_file_path", account_file_path)
    return account_file_path


def write_accounts_file(account_file_path, accounts):
    account_file_path.parent.mkdir(parents=True, exist_ok=True)
    account_file_path.write_text(json.dumps([account.model_dump() for account in accounts]))
    return account_file_path


def authorization_header(client):
    request = httpx.Request("GET", "https://example.com/public/v1/")
    return next(client.http_client.httpx_client.auth.auth_flow(request)).headers["Authorization"]


def test_binds_to_active_account(
    default_accounts_path, active_vendor_account, inactive_vendor_account
):
    write_accounts_file(default_accounts_path, [inactive_vendor_account, active_vendor_account])

    result = CLIMPTClient()

    assert result.mpt_account == active_vendor_account


def test_targets_account_environment(default_accounts_path, active_vendor_account):
    write_accounts_file(default_accounts_path, [active_vendor_account])

    result = CLIMPTClient()

    assert result.http_client.httpx_client.base_url == active_vendor_account.environment


def test_authenticates_with_account_token(default_accounts_path, active_vendor_account):
    write_accounts_file(default_accounts_path, [active_vendor_account])

    result = CLIMPTClient()

    assert authorization_header(result) == f"Bearer {active_vendor_account.token}"


def test_explicit_account_skips_accounts_file(default_accounts_path, active_vendor_account):
    result = CLIMPTClient(account=active_vendor_account)

    assert (result.mpt_account, default_accounts_path.exists()) == (
        active_vendor_account,
        False,
    )


def test_print_account_prints_bound_account(active_vendor_account, capsys):
    client = CLIMPTClient(account=active_vendor_account)

    client.print_account()  # act

    expected = f"Current active account: {active_vendor_account.id} ({active_vendor_account.name})"
    assert expected in capsys.readouterr().out


def test_file_missing_raises_error(default_accounts_path):
    with pytest.raises(CLIAccountError, match="not found"):
        CLIMPTClient()


def test_no_active_account_raises_error(default_accounts_path, inactive_vendor_account):
    write_accounts_file(default_accounts_path, [inactive_vendor_account])

    with pytest.raises(NoActiveAccountFoundError):
        CLIMPTClient()
