from cli.core.errors import MPTAPIError, wrap_mpt_api_error
from cli.core.mpt.models import (
    ListResponse,
    Meta,
    Product,
    Uom,
)
from mpt_api_client import MPTClient, RQLQuery


@wrap_mpt_api_error
def get_products(
    mpt_client: MPTClient, limit: int, offset: int, query: str | None = None
) -> ListResponse[Product]:
    """Retrieves products from the MPT Platform.

    Args:
        mpt_client: The MPTClient instance to use for the request.
        limit: The maximum number of products to retrieve.
        offset: The offset for pagination.
        query: An optional query string to filter products.

    Returns:
        A tuple containing pagination metadata and a list of Product objects.

    """
    product_collection = mpt_client.catalog.products
    if query:
        product_collection = product_collection.filter(RQLQuery.from_string(query))
    product_response = product_collection.fetch_page(limit=limit, offset=offset)
    if product_response.meta is None or product_response.meta.pagination is None:
        raise MPTAPIError("Missing pagination metadata in product response.", "Invalid response")
    pagination = product_response.meta.pagination
    return (
        Meta(limit=pagination.limit, offset=pagination.offset, total=pagination.total),
        [Product.model_validate(resource.to_dict()) for resource in product_response.resources],
    )


@wrap_mpt_api_error
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
    uom_collection = mpt_client.catalog.units_of_measure.filter(RQLQuery(name=uom_name))

    collection_page = uom_collection.fetch_page(limit=1, offset=0)

    if not collection_page.resources:
        raise MPTAPIError(f"Unit of measure by name '{uom_name}' is not found.", "404 not found")

    return Uom.model_validate(collection_page.resources[0].to_dict())
