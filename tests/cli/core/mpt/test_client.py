import pytest
from cli.core.mpt.client import MPTClient, client_from_account


def test_mpt_client_base_url():
    base_url = "https://example.com/"

    result = MPTClient(base_url, "token")

    assert result.base_url == base_url


def test_mpt_client_base_url_add_slash():
    base_url = "https://example.com"

    result = MPTClient(base_url, "token")

    assert result.base_url == f"{base_url}/"


@pytest.mark.parametrize("account_fixture", ["expected_account", "new_token_account"])
def test_mpt_client_from_client(request, account_fixture):
    expected_account = request.getfixturevalue(account_fixture)

    result = client_from_account(expected_account)

    assert result.base_url == f"{expected_account.environment}/"
    assert result.api_token == expected_account.token
