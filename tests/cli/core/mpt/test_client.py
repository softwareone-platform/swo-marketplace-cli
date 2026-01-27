import pytest
from cli.core.mpt.client import MPTClient, client_from_account


@pytest.mark.parametrize(
    ("base_url", "expected"),
    [
        ("https://example.com", "https://example.com/public/v1/"),
        ("https://example.com/", "https://example.com/public/v1/"),
    ],
)
def test_mpt_client_base_url_normalization(base_url, expected):
    result = MPTClient(base_url, "token")

    assert result.base_url == expected


@pytest.mark.parametrize("account_fixture", ["expected_account", "new_token_account"])
def test_mpt_client_from_client(request, account_fixture):
    expected_account = request.getfixturevalue(account_fixture)

    result = client_from_account(expected_account)

    assert result.base_url == f"{expected_account.environment}/public/v1/"
    assert result.api_token == expected_account.token
