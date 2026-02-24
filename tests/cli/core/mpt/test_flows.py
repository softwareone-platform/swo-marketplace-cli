import pytest
from cli.core.errors import MPTAPIError as LegacyMPTAPIError
from cli.core.mpt.flows import (
    get_products,
    search_uom_by_name,
)
from cli.core.mpt.models import (
    Product,
    Uom,
)
from mpt_api_client import RQLQuery
from mpt_api_client.exceptions import MPTAPIError, MPTHttpError


def test_get_products(api_mpt_client, mpt_products_page, mpt_products):
    api_mpt_client.catalog.products.fetch_page.return_value = mpt_products_page

    result = get_products(api_mpt_client, 10, 0)

    _meta, products = result
    assert products == [Product.model_validate(product_data) for product_data in mpt_products]


def test_get_products_with_query(api_mpt_client, mpt_products_page, mpt_products):
    product_id_rql = "eq(product.id,'PRD-1234-1234')"
    product_id_query = RQLQuery.from_string(product_id_rql)
    mock_products_filter = api_mpt_client.catalog.products.filter.return_value
    mock_products_filter.fetch_page.return_value = mpt_products_page

    result = get_products(api_mpt_client, 10, 0, product_id_query)

    _, products = result
    assert products == [Product.model_validate(product_data) for product_data in mpt_products]


def test_get_products_mpt_api_error(api_mpt_client, mock_mpt_client_error_payload):
    err_message = mock_mpt_client_error_payload["message"]
    err_status = mock_mpt_client_error_payload["status"]
    api_mpt_client.catalog.products.fetch_page.side_effect = MPTAPIError(
        err_status, err_message, mock_mpt_client_error_payload
    )

    with pytest.raises(MPTAPIError) as error:
        get_products(api_mpt_client, 10, 0)

    assert err_message in str(error.value)


def test_get_products_mpt_http_error(api_mpt_client, mock_mpt_client_error_payload):
    err_message = mock_mpt_client_error_payload["message"]
    err_status = mock_mpt_client_error_payload["status"]
    api_mpt_client.catalog.products.fetch_page.side_effect = MPTHttpError(
        err_status, err_message, mock_mpt_client_error_payload
    )

    with pytest.raises(MPTHttpError) as error:
        get_products(api_mpt_client, 10, 0)

    assert err_message in str(error.value)


def test_search_uom_by_name(mocker, api_mpt_client, mpt_uom):
    name = "User"
    uom_collection = api_mpt_client.catalog.units_of_measure
    uom_filter_result = uom_collection.filter.return_value
    uom_select = uom_filter_result.select.return_value
    uom_obj = mocker.Mock(spec=["to_dict"])
    uom_obj.to_dict.return_value = mpt_uom
    uom_select.iterate.return_value = [uom_obj]

    result = search_uom_by_name(api_mpt_client, name)

    assert result == Uom.model_validate(mpt_uom)


def test_search_uom_by_name_exception(api_mpt_client, mock_mpt_client_error_payload):
    name = "User"
    err_message = mock_mpt_client_error_payload["message"]
    uom_collection = api_mpt_client.catalog.units_of_measure
    uom_filter_result = uom_collection.filter.return_value
    uom_select = uom_filter_result.select.return_value
    uom_select.iterate.side_effect = LegacyMPTAPIError(err_message, err_message)

    with pytest.raises(LegacyMPTAPIError) as error:
        search_uom_by_name(api_mpt_client, name)

    assert err_message in str(error.value)


def test_search_uom_by_name_not_found(api_mpt_client):
    name = "User"
    uom_collection = api_mpt_client.catalog.units_of_measure
    uom_filter_result = uom_collection.filter.return_value
    uom_select = uom_filter_result.select.return_value
    uom_select.iterate.return_value = []

    with pytest.raises(LegacyMPTAPIError) as error:
        search_uom_by_name(api_mpt_client, name)

    assert "is not found" in str(error.value)
