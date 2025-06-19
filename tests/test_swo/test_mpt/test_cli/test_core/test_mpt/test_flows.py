from urllib.parse import urljoin

import pytest
from responses import matchers
from swo.mpt.cli.core.errors import MPTAPIError
from swo.mpt.cli.core.mpt.flows import (
    create_item,
    create_item_group,
    create_parameter,
    create_parameter_group,
    create_template,
    get_products,
    get_token,
    search_uom_by_name,
)
from swo.mpt.cli.core.mpt.models import (
    Item,
    ItemGroup,
    Parameter,
    ParameterGroup,
    Product,
    Template,
    Token,
    Uom,
)


def test_get_token(requests_mocker, mpt_client, mpt_token, wrap_to_mpt_list_response):
    secret = "id123456789"
    requests_mocker.get(
        urljoin(mpt_client.base_url, f"/accounts/api-tokens?limit=2&token={secret}"),
        json=wrap_to_mpt_list_response([mpt_token]),
    )

    token = get_token(mpt_client, secret)

    assert token == Token.model_validate(mpt_token)


def test_get_token_exception_zero_tokens(requests_mocker, mpt_client, wrap_to_mpt_list_response):
    secret = "id123456789"
    requests_mocker.get(
        urljoin(mpt_client.base_url, f"/accounts/api-tokens?limit=2&token={secret}"),
        json=wrap_to_mpt_list_response([]),
    )

    with pytest.raises(MPTAPIError) as e:
        get_token(mpt_client, secret)

    assert "MPT API for Tokens returns 0 or more than 1 tokens for secret" in str(e.value)


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

    assert "MPT API for Tokens returns 0 or more than 1 tokens for secret" in str(e.value)


def test_get_products(requests_mocker, mpt_client, mpt_products_response, mpt_products):
    requests_mocker.get(
        urljoin(mpt_client.base_url, "/catalog/products?limit=10&offset=0"),
        json=mpt_products_response,
    )

    meta, products = get_products(mpt_client, 10, 0)

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


def test_create_parameter_group(requests_mocker, mpt_client, product, mpt_parameter_group):
    requests_mocker.post(
        urljoin(mpt_client.base_url, f"/catalog/products/{product.id}/parameter-groups"),
        json=mpt_parameter_group,
        match=[matchers.json_params_matcher({"name": "Parameter Group"})],
    )

    group = create_parameter_group(mpt_client, product, {"name": "Parameter Group"})

    assert group == ParameterGroup.model_validate(mpt_parameter_group)


def test_create_parameter_group_exception(requests_mocker, mpt_client, product):
    requests_mocker.post(
        urljoin(mpt_client.base_url, f"/catalog/products/{product.id}/parameter-groups"),
        status=500,
    )

    with pytest.raises(MPTAPIError) as e:
        create_parameter_group(mpt_client, product, {"name": "Parameter Group"})

    assert "Internal Server Error" in str(e.value)


def test_create_item_group(requests_mocker, mpt_client, product, mpt_item_group):
    requests_mocker.post(
        urljoin(mpt_client.base_url, f"/catalog/products/{product.id}/item-groups"),
        json=mpt_item_group,
        match=[matchers.json_params_matcher({"name": "Item Group"})],
    )

    group = create_item_group(mpt_client, product, {"name": "Item Group"})

    assert group == ItemGroup.model_validate(mpt_item_group)


def test_create_item_group_exception(requests_mocker, mpt_client, product):
    requests_mocker.post(
        urljoin(mpt_client.base_url, f"/catalog/products/{product.id}/item-groups"),
        status=500,
    )

    with pytest.raises(MPTAPIError) as e:
        create_item_group(mpt_client, product, {"name": "Item Group"})

    assert "Internal Server Error" in str(e.value)


def test_create_parameter(requests_mocker, mpt_client, product, mpt_parameter):
    requests_mocker.post(
        urljoin(mpt_client.base_url, f"/catalog/products/{product.id}/parameters"),
        json=mpt_parameter,
        match=[matchers.json_params_matcher({"name": "Parameter Name"})],
    )

    group = create_parameter(mpt_client, product, {"name": "Parameter Name"})

    assert group == Parameter.model_validate(mpt_parameter)


def test_create_parameter_exception(requests_mocker, mpt_client, product):
    requests_mocker.post(
        urljoin(mpt_client.base_url, f"/catalog/products/{product.id}/parameters"), status=500
    )

    with pytest.raises(MPTAPIError) as e:
        create_parameter(mpt_client, product, {"name": "Parameter Name"})

    assert "Internal Server Error" in str(e.value)


def test_create_item(requests_mocker, mpt_client, mpt_item):
    requests_mocker.post(
        urljoin(mpt_client.base_url, "/catalog/items"),
        json=mpt_item,
        match=[matchers.json_params_matcher({"name": "Item Name"})],
    )

    group = create_item(mpt_client, {"name": "Item Name"})

    assert group == Item.model_validate(mpt_item)


def test_create_item_exception(requests_mocker, mpt_client):
    requests_mocker.post(urljoin(mpt_client.base_url, "/catalog/items"), status=500)

    with pytest.raises(MPTAPIError) as e:
        create_item(mpt_client, {"name": "Item Name"})

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


def test_create_template(requests_mocker, mpt_client, product, mpt_template):
    requests_mocker.post(
        urljoin(
            mpt_client.base_url,
            f"/catalog/products/{product.id}/templates",
        ),
        json=mpt_template,
        match=[matchers.json_params_matcher({"name": "Template Name"})],
    )

    template = create_template(mpt_client, product, {"name": "Template Name"})

    assert template == Template.model_validate(mpt_template)


def test_create_template_exception(requests_mocker, product, mpt_client):
    requests_mocker.post(
        urljoin(mpt_client.base_url, f"/catalog/products/{product.id}/templates"), status=500
    )

    with pytest.raises(MPTAPIError) as e:
        create_template(mpt_client, product, {"name": "Template Name"})

    assert "Internal Server Error" in str(e.value)


def test_create_template_400_exception(requests_mocker, product, mpt_client):
    requests_mocker.post(
        urljoin(mpt_client.base_url, f"/catalog/products/{product.id}/templates"),
        status=400,
        json={"errors": {"description": ["error for exception"]}},
    )

    with pytest.raises(MPTAPIError) as e:
        create_template(mpt_client, product, {"name": "Template Name"})

    assert "error for exception" in str(e.value)
