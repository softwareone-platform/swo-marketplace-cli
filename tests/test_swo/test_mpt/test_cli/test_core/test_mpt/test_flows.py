from urllib.parse import urljoin

import pytest
from swo.mpt.cli.core.errors import MPTAPIError
from swo.mpt.cli.core.mpt.flows import get_products, get_token
from swo.mpt.cli.core.mpt.models import Product, Token


def test_get_token(requests_mocker, mpt_client, mpt_token, wrap_to_mpt_list_response):
    secret = "id123456789"
    requests_mocker.get(
        urljoin(mpt_client.base_url, f"/accounts/api-tokens?limit=2&token={secret}"),
        json=wrap_to_mpt_list_response([mpt_token]),
    )

    token = get_token(mpt_client, secret)

    assert token == Token.model_validate(mpt_token)


def test_get_token_exception_zero_tokens(
    requests_mocker, mpt_client, wrap_to_mpt_list_response
):
    secret = "id123456789"
    requests_mocker.get(
        urljoin(mpt_client.base_url, f"/accounts/api-tokens?limit=2&token={secret}"),
        json=wrap_to_mpt_list_response([]),
    )

    with pytest.raises(MPTAPIError) as e:
        get_token(mpt_client, secret)

    assert "MPT API for Tokens returns 0 or more than 1 tokens for secret" in str(
        e.value
    )


def test_get_token_exception_more_than_one(
    requests_mocker, mpt_client, mpt_token, wrap_to_mpt_list_response
):
    secret = "id123456789"
    requests_mocker.get(
        urljoin(mpt_client.base_url, f"/accounts/api-tokens?limit=2&token={secret}"),
        json=wrap_to_mpt_list_response([mpt_token, mpt_token]),
    )

    with pytest.raises(MPTAPIError) as e:
        get_token(mpt_client, secret)

    assert "MPT API for Tokens returns 0 or more than 1 tokens for secret" in str(
        e.value
    )


def test_get_products(requests_mocker, mpt_client, mpt_products_response, mpt_products):
    requests_mocker.get(
        urljoin(mpt_client.base_url, "/products?limit=10&offset=0"),
        json=mpt_products_response,
    )

    meta, products = get_products(mpt_client, 10, 0)

    assert products == [Product.model_validate(p) for p in mpt_products]


def test_get_products_with_query(
    requests_mocker, mpt_client, mpt_products_response, mpt_products
):
    requests_mocker.get(
        urljoin(
            mpt_client.base_url,
            "/products?limit=10&offset=0&eq(product.id,PRD-1234-1234)",
        ),
        json=mpt_products_response,
    )

    meta, products = get_products(mpt_client, 10, 0)

    assert products == [Product.model_validate(p) for p in mpt_products]


def test_get_products_exception(requests_mocker, mpt_client):
    requests_mocker.get(
        urljoin(mpt_client.base_url, "/products?limit=10&offset=0"),
        status=500,
    )

    with pytest.raises(MPTAPIError) as e:
        get_products(mpt_client, 10, 0)

    assert "Internal Server Error" in str(e.value)
