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


@pytest.mark.parametrize(
    ("query", "expected_resource"),
    [
        (None, "catalog/products?limit=10&offset=0"),
        (
            "eq(product.id,'PRD-1234-1234')",
            "catalog/products?limit=10&offset=0&eq%28product.id%2C%27PRD-1234-1234%27%29",
        ),
    ],
)
def test_get_products(
    query, expected_resource, requests_mocker, mpt_client, mpt_products_response, mpt_products
):
    requests_mocker.get(urljoin(mpt_client.base_url, expected_resource), json=mpt_products_response)

    result = get_products(mpt_client, 10, 0, query=query)

    _meta, products = result
    assert products == [Product.model_validate(product_data) for product_data in mpt_products]


def test_get_products_exception(requests_mocker, mpt_client):
    requests_mocker.get(
        urljoin(mpt_client.base_url, "catalog/products?limit=10&offset=0"), status=500
    )

    with pytest.raises(MPTAPIError) as error:
        get_products(mpt_client, 10, 0)

    assert "Internal Server Error" in str(error.value)


def test_search_uom_by_name(requests_mocker, mpt_client, mpt_uom, mpt_uoms_response):
    name = "User"
    requests_mocker.get(
        urljoin(
            mpt_client.base_url,
            f"catalog/units-of-measure?name={name}&limit=1&offset=0",
        ),
        json=mpt_uoms_response,
    )

    result = search_uom_by_name(mpt_client, name)

    assert result == Uom.model_validate(mpt_uom)


def test_search_uom_by_name_exception(requests_mocker, mpt_client):
    name = "User"
    requests_mocker.get(
        urljoin(
            mpt_client.base_url,
            f"catalog/units-of-measure?name={name}&limit=1&offset=0",
        ),
        status=500,
    )

    with pytest.raises(MPTAPIError) as error:
        search_uom_by_name(mpt_client, name)

    assert "Internal Server Error" in str(error.value)


def test_search_uom_by_name_not_found(requests_mocker, wrap_to_mpt_list_response, mpt_client):
    name = "User"
    requests_mocker.get(
        urljoin(
            mpt_client.base_url,
            f"catalog/units-of-measure?name={name}&limit=1&offset=0",
        ),
        json=wrap_to_mpt_list_response([]),
    )

    with pytest.raises(MPTAPIError) as error:
        search_uom_by_name(mpt_client, name)

    assert "is not found" in str(error.value)
