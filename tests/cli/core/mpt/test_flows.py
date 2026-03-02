import pytest
from cli.core.errors import MPTAPIError
from cli.core.mpt.flows import get_products, search_uom_by_name
from cli.core.mpt.models import Product, Uom
from mpt_api_client.exceptions import MPTAPIError as ClientAPIError
from mpt_api_client.models import Collection, Meta, Model, Pagination


@pytest.mark.parametrize(
    "query",
    [
        None,
        "eq(product.id,'PRD-1234-1234')",
    ],
)
def test_get_products(mocker, mock_mpt_api_client, mpt_products, query):
    mock_resources = []
    for product_data in mpt_products:
        resource = mocker.MagicMock(spec=Model)
        resource.to_dict.return_value = product_data
        mock_resources.append(resource)
    collection = mocker.MagicMock(spec=Collection)
    collection.meta = mocker.MagicMock(spec=Meta)
    collection.meta.pagination = mocker.MagicMock(spec=Pagination)
    collection.meta.pagination.limit = 10
    collection.meta.pagination.offset = 0
    collection.meta.pagination.total = len(mpt_products)
    collection.resources = mock_resources
    mock_mpt_api_client.catalog.products.fetch_page.return_value = collection
    product_filter = mock_mpt_api_client.catalog.products.filter.return_value
    product_filter.fetch_page.return_value = collection

    result = get_products(mock_mpt_api_client, 10, 0, query)

    _, products = result
    assert products == [Product.model_validate(product_data) for product_data in mpt_products]


def test_get_products_exception(mock_mpt_api_client, mock_mpt_client_error_payload):
    mock_mpt_api_client.catalog.products.fetch_page.side_effect = ClientAPIError(
        mock_mpt_client_error_payload["status"],
        mock_mpt_client_error_payload["message"],
        mock_mpt_client_error_payload,
    )

    with pytest.raises(MPTAPIError) as error:
        get_products(mock_mpt_api_client, 10, 0)

    assert "Internal Server Error" in str(error.value)


def test_get_products_missing_meta(mocker, mock_mpt_api_client):
    collection = mocker.MagicMock(spec=Collection)
    collection.meta = None
    mock_mpt_api_client.catalog.products.fetch_page.return_value = collection

    with pytest.raises(MPTAPIError) as error:
        get_products(mock_mpt_api_client, 10, 0)

    assert "Missing pagination metadata" in str(error.value)


def test_search_uom_by_name(mock_mpt_api_client, mpt_uom, mocker):
    resource = mocker.MagicMock(spec=Model)
    resource.to_dict.return_value = mpt_uom
    collection = mocker.MagicMock(spec=Collection)
    collection.resources = [resource]
    uom_filter = mock_mpt_api_client.catalog.units_of_measure.filter.return_value
    uom_filter.fetch_page.return_value = collection

    result = search_uom_by_name(mock_mpt_api_client, "User")

    assert result == Uom.model_validate(mpt_uom)


def test_search_uom_by_name_exception(mock_mpt_api_client, mock_mpt_client_error_payload):
    uom_filter = mock_mpt_api_client.catalog.units_of_measure.filter.return_value
    uom_filter.fetch_page.side_effect = ClientAPIError(
        mock_mpt_client_error_payload["status"],
        mock_mpt_client_error_payload["message"],
        mock_mpt_client_error_payload,
    )

    with pytest.raises(MPTAPIError) as error:
        search_uom_by_name(mock_mpt_api_client, "User")

    assert "Internal Server Error" in str(error.value)


def test_search_uom_by_name_not_found(mock_mpt_api_client, mocker):
    collection = mocker.MagicMock(spec=Collection)
    collection.resources = []
    uom_filter = mock_mpt_api_client.catalog.units_of_measure.filter.return_value
    uom_filter.fetch_page.return_value = collection

    with pytest.raises(MPTAPIError) as error:
        search_uom_by_name(mock_mpt_api_client, "User")

    assert "is not found" in str(error.value)
