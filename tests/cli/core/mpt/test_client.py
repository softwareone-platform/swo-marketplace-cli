import logging

import pytest
from cli.core.accounts.models import Account
from cli.core.mpt.client import MPTClient, client_from_account
from cli.core.state import state
from requests import Request


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


def test_join_url_with_leading_slash():
    client = MPTClient("https://example.com", "token")

    result = client.join_url("/products")

    assert result == "https://example.com/public/v1/products"


def test_request_makes_http_call(requests_mocker):
    requests_mocker.add("GET", "https://example.com/public/v1/products", json={}, status=200)
    client = MPTClient("https://example.com", "token")

    result = client.request("GET", "products")

    assert result.status_code == 200


def test_request_with_debug_logging(requests_mocker, caplog):
    requests_mocker.add(
        "GET", "https://example.com/public/v1/products", json={"id": "1"}, status=200
    )
    client = MPTClient("https://example.com", "token", debug=True)

    with caplog.at_level(logging.DEBUG, logger="cli.core.mpt.client"):
        result = client.request("GET", "products")

    assert result.status_code == 200
    assert "HTTP Request" in caplog.text
    assert "Response Status" in caplog.text


def test_prepare_request_joins_url():
    client = MPTClient("https://example.com", "token")
    request = Request("GET", "products")

    result = client.prepare_request(request)

    assert result.url == "https://example.com/public/v1/products"
