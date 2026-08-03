import pytest
from cli.core.mpt.models import Meta, Product
from cli.core.products import app as product_app
from typer.testing import CliRunner

runner = CliRunner()


@pytest.fixture
def mock_mpt_client(mocker):
    return mocker.patch("cli.core.products.app.list_products.CLIMPTClient", autospec=True)


def test_list_products(mock_mpt_client, mocker, mpt_products_response):
    mocker.patch(
        "cli.core.products.app.list_products.get_products",
        return_value=(
            Meta(limit=10, offset=0, total=2),
            [
                Product.model_validate(product_data)
                for product_data in mpt_products_response["data"]
            ],
        ),
    )

    result = runner.invoke(product_app, ["list"])

    assert result.exit_code == 0, result.stdout
    assert mpt_products_response["data"][0]["id"] in result.stdout


def test_list_products_paginates(mock_mpt_client, mocker, mpt_products_response):
    products = [Product.model_validate(record) for record in mpt_products_response["data"]]
    get_products_mock = mocker.patch(
        "cli.core.products.app.list_products.get_products",
        side_effect=[
            (Meta(limit=1, offset=0, total=2), products[:1]),
            (Meta(limit=1, offset=1, total=2), products[1:]),
        ],
    )

    result = runner.invoke(product_app, ["list", "--page", "1"], input="y\n")

    assert result.exit_code == 0, result.stdout
    assert get_products_mock.call_count == 2
    assert mpt_products_response["data"][1]["id"] in result.stdout


def test_list_products_with_query_and_paging(mock_mpt_client, mocker, mpt_products_response):
    mocker.patch(
        "cli.core.products.app.list_products.get_products",
        return_value=(
            Meta(limit=24, offset=0, total=2),
            [
                Product.model_validate(product_data)
                for product_data in mpt_products_response["data"]
            ],
        ),
    )

    result = runner.invoke(
        product_app,
        ["list", "--page", "24", "--query", "eq(product.id,'PRD-1234')"],
    )

    assert result.exit_code == 0, result.stdout
    assert mpt_products_response["data"][0]["id"] in result.stdout
