from urllib.parse import urljoin

import pytest
from swo.mpt.cli.core.mpt.client import MPTClient, client_from_account


def test_mpt_client_base_url():
    base_url = "https://example.com/"

    mpt_client = MPTClient(base_url, "token")

    assert mpt_client.base_url == base_url


def test_mpt_client_base_url_add_slash():
    base_url = "https://example.com"

    mpt_client = MPTClient(base_url, "token")

    assert mpt_client.base_url == f"{base_url}/"


def test_mpt_client_url_join(requests_mocker):
    mpt_client = MPTClient("https://example.com/", "token")
    requests_mocker.get(
        urljoin(mpt_client.base_url, "commerce/orders/ORD-0000/fail"),
    )

    mpt_client.get("commerce/orders/ORD-0000/fail")


def test_mpt_client_url_join_slash(requests_mocker):
    mpt_client = MPTClient("https://example.com/", "token")
    requests_mocker.get(
        urljoin(mpt_client.base_url, "/commerce/orders/ORD-0000/fail"),
    )

    mpt_client.get("/commerce/orders/ORD-0000/fail")


@pytest.mark.parametrize("account_fixture", ["expected_account", "new_token_account"])
def test_mpt_client_from_client(request, account_fixture):
    expected_account = request.getfixturevalue(account_fixture)
    mpt_client = client_from_account(expected_account)

    assert mpt_client.base_url == f"{expected_account.environment}/"
    assert mpt_client.api_token == expected_account.token
