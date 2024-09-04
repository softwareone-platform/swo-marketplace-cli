import json
from functools import cache
from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus

from requests_toolbelt import MultipartEncoder  # type: ignore
from swo.mpt.cli.core.errors import MPTAPIError, wrap_http_error

from .client import MPTClient
from .models import (
    Item,
    ItemGroup,
    ListResponse,
    Meta,
    Parameter,
    ParameterGroup,
    Pricelist,
    PricelistItem,
    Product,
    Template,
    Token,
    Uom,
)


@wrap_http_error
def get_token(mpt_client: MPTClient, secret: str) -> Token:
    """
    Retrieves API Token from the MPT Platform
    """
    response = mpt_client.get(f"/accounts/api-tokens?limit=2&token={secret}")
    response.raise_for_status()

    response_body = response.json()

    if len(response_body["data"]) == 0 or len(response_body["data"]) > 1:
        raise MPTAPIError(
            f"MPT API for Tokens returns 0 or more than 1 tokens for secret {secret}",
            "\n" + json.dumps(response_body),
        )

    return Token.model_validate(response_body["data"][0])


@wrap_http_error
def get_products(
    mpt_client: MPTClient, limit: int, offset: int, query: Optional[str] = None
) -> ListResponse[Product]:
    """
    Retrieves Products from the MPT Platform
    """
    url = f"/catalog/products?limit={quote_plus(str(limit))}&offset={quote_plus(str(offset))}"

    if query:
        url = f"{url}&{quote_plus(query)}"

    response = mpt_client.get(url)
    response.raise_for_status()

    json_body = response.json()

    return (
        Meta.model_validate(json_body["$meta"]["pagination"]),
        [Product.model_validate(p) for p in json_body["data"]],
    )


@wrap_http_error
def create_product(
    mpt_client: MPTClient, product_json: dict, settings_json: dict, icon: Path
) -> Product:
    parameters = MultipartEncoder(
        fields={
            "product": json.dumps(product_json),
            "icon": ("icon.png", open(icon, "rb"), "image/png"),
        }
    )

    products_response = mpt_client.post(
        "/catalog/products", data=parameters, headers={"Content-Type": parameters.content_type}
    )
    products_response.raise_for_status()
    product = Product.model_validate(products_response.json())

    response = mpt_client.put(
        f"/catalog/products/{product.id}/settings",
        json=settings_json,
    )
    response.raise_for_status()

    return product


@wrap_http_error
def create_parameter_group(
    mpt_client: MPTClient, product: Product, parameter_group_json: dict
) -> ParameterGroup:
    response = mpt_client.post(
        f"/catalog/products/{product.id}/parameter-groups", json=parameter_group_json
    )
    response.raise_for_status()

    return ParameterGroup.model_validate(response.json())


@wrap_http_error
def create_item_group(
    mpt_client: MPTClient, product: Product, item_group_json: dict
) -> ItemGroup:
    response = mpt_client.post(
        f"/catalog/products/{product.id}/item-groups", json=item_group_json
    )
    response.raise_for_status()

    return ItemGroup.model_validate(response.json())


@wrap_http_error
def create_parameter(
    mpt_client: MPTClient, product: Product, parameter_json: dict
) -> Parameter:
    response = mpt_client.post(
        f"/catalog/products/{product.id}/parameters", json=parameter_json
    )
    response.raise_for_status()

    return Parameter.model_validate(response.json())


@wrap_http_error
def create_item(mpt_client: MPTClient, item_json: dict) -> Item:
    response = mpt_client.post("/catalog/items", json=item_json)
    response.raise_for_status()

    return Item.model_validate(response.json())


@wrap_http_error
def review_item(mpt_client: MPTClient, item_id: str) -> None:
    response = mpt_client.post(f"/catalog/items/{item_id}/review")
    response.raise_for_status()


@wrap_http_error
def publish_item(mpt_client: MPTClient, item_id: str) -> None:
    response = mpt_client.post(f"/catalog/items/{item_id}/publish")
    response.raise_for_status()


@wrap_http_error
def unpublish_item(mpt_client: MPTClient, item_id: str) -> None:
    response = mpt_client.post(f"/catalog/items/{item_id}/unpublish")
    response.raise_for_status()


@wrap_http_error
def update_item(mpt_client, item_id: str, item_json: dict) -> None:
    response = mpt_client.put(f"/catalog/items/{item_id}", json=item_json)
    response.raise_for_status()


@wrap_http_error
def get_item(mpt_client: MPTClient, product_id: str, vendor_id: str) -> Item:
    response = mpt_client.get(
        f"/catalog/items?externalIds.vendor={vendor_id}&product.id={product_id}&limit=1&offset=0"
    )
    response.raise_for_status()

    data = response.json()["data"]
    if not data:
        raise MPTAPIError(
            f"Item by Item Vendor ID '{vendor_id}' is not found.",
            "404 not found",
        )

    return Item.model_validate(data[0])


@cache
@wrap_http_error
def search_uom_by_name(mpt_client: MPTClient, uom_name: str) -> Uom:
    response = mpt_client.get(f"/catalog/units-of-measure?name={uom_name}&limit=1&offset=0")
    response.raise_for_status()

    data = response.json()["data"]
    if not data:
        raise MPTAPIError(
            f"Unit of measure by name '{uom_name}' is not found.",
            "404 not found",
        )

    return Uom.model_validate(data[0])


@wrap_http_error
def create_template(
    mpt_client: MPTClient, product: Product, template_json: dict
) -> Template:
    response = mpt_client.post(f"/catalog/products/{product.id}/templates", json=template_json)
    response.raise_for_status()

    return Template.model_validate(response.json())


@wrap_http_error
def get_pricelist(mpt_client: MPTClient, pricelist_id: str) -> Pricelist:
    response = mpt_client.get(f"/catalog/price-lists/{pricelist_id}")
    response.raise_for_status()

    return Pricelist.model_validate(response.json())


@wrap_http_error
def create_pricelist(mpt_client: MPTClient, pricelist_json: dict) -> Pricelist:
    response = mpt_client.post("/catalog/price-lists", json=pricelist_json)
    response.raise_for_status()

    return Pricelist.model_validate(response.json())


@wrap_http_error
def update_pricelist(
    mpt_client: MPTClient, pricelist_id: str, pricelist_json: dict
) -> Pricelist:
    response = mpt_client.put(f"/catalog/price-lists/{pricelist_id}", json=pricelist_json)
    response.raise_for_status()

    return Pricelist.model_validate(response.json())


@wrap_http_error
def get_pricelist_item(
    mpt_client: MPTClient, pricelist_id: str, vendor_id: str
) -> PricelistItem:
    response = mpt_client.get(
        f"/catalog/price-lists/{pricelist_id}/items?item.externalIds.vendor={vendor_id}&limit=1&offset=0"
    )
    response.raise_for_status()

    data = response.json()["data"]
    if not data:
        raise MPTAPIError(
            f"Pricelist Item by Item Vendor ID '{vendor_id}' is not found.",
            "404 not found",
        )

    return PricelistItem.model_validate(data[0])


@wrap_http_error
def update_pricelist_item(
    mpt_client: MPTClient,
    pricelist_id: str,
    pricelist_item_id: str,
    pricelist_item_json: dict,
) -> PricelistItem:
    response = mpt_client.put(
        f"/catalog/price-lists/{pricelist_id}/items/{pricelist_item_id}",
        json=pricelist_item_json,
    )
    response.raise_for_status()

    return PricelistItem.model_validate(response.json())
