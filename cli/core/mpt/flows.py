from dataclasses import asdict
from functools import cache

from cli.core.errors import MPTAPIError, wrap_http_error
from cli.core.mpt.models import (
    ListResponse,
    Meta,
    Product,
    Uom,
)
from mpt_api_client import MPTClient, RQLQuery


@wrap_http_error
def get_products(
    api_mpt_client: MPTClient, limit: int, offset: int, query: RQLQuery | None = None
) -> ListResponse[Product]:
    """Retrieves products from the MPT Platform.

    Args:
        api_mpt_client: The MPTClient instance to use for the request.
        limit: The maximum number of products to retrieve.
        offset: The offset for pagination.
        query: An optional RQLQuery object to filter products.

    Returns:
        A tuple containing pagination metadata and a list of Product objects.

    """
    products_collection = api_mpt_client.catalog.products

    if query:
        products_collection = products_collection.filter(query)

    paginated_products_collection = products_collection.fetch_page(limit=limit, offset=offset)

    meta_response_data = paginated_products_collection.meta.pagination  # type: ignore[union-attr]

    product_response_data = paginated_products_collection.to_list()

    return (
        Meta.model_validate(asdict(meta_response_data)),
        [Product.model_validate(product_data) for product_data in product_response_data],
    )


@cache
@wrap_http_error
def search_uom_by_name(mpt_client: MPTClient, uom_name: str) -> Uom:
    """Searches for a unit of measure by name using the MPT Platform.

    Args:
        mpt_client: The MPTClient instance to use for the request.
        uom_name: The name of the unit of measure to search for.

    Returns:
        The Uom object matching the provided name.

    Raises:
        MPTAPIError: If the unit of measure is not found.

    """
    name_query = RQLQuery(name=uom_name)
    uom_collection = mpt_client.catalog.units_of_measure
    uom_data_response = uom_collection.filter(name_query).select()
    uom_result = list(uom_data_response.iterate())

    if not uom_result:
        raise MPTAPIError(f"Unit of measure by name '{uom_name}' is not found.", "404 not found")

    return Uom.model_validate(uom_result[0].to_dict())
