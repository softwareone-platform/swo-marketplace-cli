import json
from typing import Optional
from urllib.parse import quote_plus

from swo.mpt.cli.core.errors import MPTAPIError, wrap_http_error

from .client import MPTClient
from .models import ListResponse, Meta, Product, Token


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
    url = f"/products?limit={quote_plus(str(limit))}&offset={quote_plus(str(offset))}"

    if query:
        url = f"{url}&{quote_plus(query)}"

    response = mpt_client.get(url)
    response.raise_for_status()

    json_body = response.json()

    return (
        Meta.model_validate(json_body["$meta"]["pagination"]),
        [Product.model_validate(p) for p in json_body["data"]],
    )
