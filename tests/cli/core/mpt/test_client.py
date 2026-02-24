import pytest
from cli.core.accounts.models import Account
from cli.core.mpt.client import MPTClient, client_from_account
from cli.core.state import state


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


def test_mpt_client_from_client(mocker):
    mocker.patch.object(state, "verbose", False)  # noqa: FBT003
    account = Account(
        id="ACC-12341",
        name="Account 1",
        type="Vendor",
        token="fake-token",  # noqa: S106
        token_id="TKN-1111-1111",  # noqa: S106
        environment="https://example.com",
        is_active=True,
    )

    result = client_from_account(account)

    assert isinstance(result, MPTClient)
    assert result.api_token == account.token
    assert result.base_url == "https://example.com/public/v1/"
    assert result.debug is False
