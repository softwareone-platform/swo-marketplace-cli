from urllib.parse import urljoin

import pytest
from cli.core.errors import MPTAPIError
from cli.core.mpt.flows import (
    get_products,
    search_uom_by_name,
)
from cli.core.mpt.models import (
    Product,
    Uom,
)


def test_get_products(requests_mocker, mpt_client, mpt_products_response, mpt_products):
    requests_mocker.get(
        urljoin(mpt_client.base_url, "/catalog/products?limit=10&offset=0"),
        json=mpt_products_response,
    )

    _meta, products = get_products(mpt_client, 10, 0)

    assert products == [Product.model_validate(p) for p in mpt_products]


def test_get_products_with_query(requests_mocker, mpt_client, mpt_products_response, mpt_products):
    requests_mocker.get(
        urljoin(
            mpt_client.base_url,
            "/catalog/products?limit=10&offset=0&eq(product.id,PRD-1234-1234)",
        ),
        json=mpt_products_response,
    )

    _, products = get_products(mpt_client, 10, 0)

    assert products == [Product.model_validate(p) for p in mpt_products]


def test_get_products_exception(requests_mocker, mpt_client):
    requests_mocker.get(
        urljoin(mpt_client.base_url, "/catalog/products?limit=10&offset=0"),
        status=500,
    )

    with pytest.raises(MPTAPIError) as e:
        get_products(mpt_client, 10, 0)

    assert "Internal Server Error" in str(e.value)


def test_search_uom_by_name(requests_mocker, mpt_client, mpt_uom, mpt_uoms_response):
    name = "User"
    requests_mocker.get(
        urljoin(mpt_client.base_url, f"/catalog/units-of-measure?name={name}&limit=1&offset=0"),
        json=mpt_uoms_response,
    )

    uom = search_uom_by_name(mpt_client, name)

    assert uom == Uom.model_validate(mpt_uom)


def test_search_uom_by_name_exception(requests_mocker, mpt_client):
    name = "User"
    requests_mocker.get(
        urljoin(mpt_client.base_url, f"/catalog/units-of-measure?name={name}&limit=1&offset=0"),
        status=500,
    )

    with pytest.raises(MPTAPIError) as e:
        search_uom_by_name(mpt_client, name)

    assert "Internal Server Error" in str(e.value)


def test_search_uom_by_name_not_found(requests_mocker, wrap_to_mpt_list_response, mpt_client):
    name = "User"
    requests_mocker.get(
        urljoin(mpt_client.base_url, f"/catalog/units-of-measure?name={name}&limit=1&offset=0"),
        json=wrap_to_mpt_list_response([]),
    )

    with pytest.raises(MPTAPIError) as e:
        search_uom_by_name(mpt_client, name)

    assert "is not found" in str(e.value)
