from functools import cache
from urllib.parse import quote_plus

from cli.core.errors import MPTAPIError, wrap_http_error

from .client import MPTClient
from .models import (
    ListResponse,
    Meta,
    Product,
    Uom,
)


@wrap_http_error
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
    url = f"/catalog/products?limit={quote_plus(str(limit))}&offset={quote_plus(str(offset))}"
    if query:
        url = f"{url}&{quote_plus(query)}"
    response = mpt_client.get(url)
    response.raise_for_status()
    json_body = response.json()
    return (
        Meta.model_validate(json_body["$meta"]["pagination"]),
        [Product.model_validate(product_data) for product_data in json_body["data"]],
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
    response = mpt_client.get(f"/catalog/units-of-measure?name={uom_name}&limit=1&offset=0")
    response.raise_for_status()

    response_data = response.json()["data"]
    if not response_data:
        raise MPTAPIError(f"Unit of measure by name '{uom_name}' is not found.", "404 not found")

    return Uom.model_validate(response_data[0])
