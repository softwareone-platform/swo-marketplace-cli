from urllib.parse import urljoin

from swo.mpt.cli.core.products import app
from typer.testing import CliRunner

runner = CliRunner()


def test_list_products(
    expected_account, mocker, requests_mocker, mpt_client, mpt_products_response
):
    mocker.patch("swo.mpt.cli.core.products.app.get_active_account", return_value=expected_account)
    requests_mocker.get(
        urljoin(
            mpt_client.base_url,
            "/catalog/products?limit=10&offset=0",
            allow_fragments=True,
        ),
        json=mpt_products_response,
    )

    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0, result.stdout
    assert mpt_products_response["data"][0]["id"] in result.stdout


def test_list_products_with_query_and_paging(
    expected_account, mocker, requests_mocker, mpt_client, mpt_products_response
):
    mocker.patch("swo.mpt.cli.core.products.app.get_active_account", return_value=expected_account)
    requests_mocker.get(
        urljoin(
            mpt_client.base_url,
            "/catalog/products?limit=20&offset=0&eq(product.id,PRD-1234)",
            allow_fragments=True,
        ),
        json=mpt_products_response,
    )

    result = runner.invoke(
        app,
        ["list", "--page", "20", "--query", "eq(product.id,PRD-1234)"],
    )

    assert result.exit_code == 0, result.stdout
    assert mpt_products_response["data"][0]["id"] in result.stdout


def test_file_with_extension(expected_account, mocker):
    mocker.patch("swo.mpt.cli.core.products.app.get_active_account", return_value=expected_account)


def test_sync_file_doesnt_exist(expected_account, mocker):
    mocker.patch("swo.mpt.cli.core.products.app.get_active_account", return_value=expected_account)

    result = runner.invoke(
        app,
        ["sync", "--dry-run", "some-file"],
    )

    assert result.exit_code == 3, result.stdout
    assert "Provided file path doesn't exist" in result.stdout


def test_sync_with_dry_run_failure(expected_account, mocker, empty_file):
    mocker.patch("swo.mpt.cli.core.products.app.get_active_account", return_value=expected_account)

    result = runner.invoke(
        app,
        ["sync", "--dry-run", str(empty_file)],
    )

    assert result.exit_code == 3, result.stdout
    assert "General: Required tab doesn't exist" in result.stdout


def test_sync_with_dry_run(expected_account, mocker, new_product_file):
    mocker.patch("swo.mpt.cli.core.products.app.get_active_account", return_value=expected_account)

    result = runner.invoke(
        app,
        ["sync", "--dry-run", str(new_product_file)],
    )

    assert result.exit_code == 0, result.stdout
    assert "Product definition" in result.stdout


def test_sync_product_update(
    mocker, expected_account, mock_sync_product, new_product_file, product
):
    mocker.patch("swo.mpt.cli.core.products.app.check_product_exists", return_value=product)
    mocker.patch("swo.mpt.cli.core.products.app.get_active_account", return_value=expected_account)

    result = runner.invoke(
        app,
        ["sync", str(new_product_file)],
        input="y\n",
    )

    assert result.exit_code == 0, result.stdout
    assert "Do you want to update product" in result.stdout
    assert "Product Sync" in result.stdout


def test_sync_product_force_create(
    mocker, expected_account, mock_sync_product, new_product_file, product
):
    mocker.patch("swo.mpt.cli.core.products.app.check_product_exists", return_value=product)
    mocker.patch("swo.mpt.cli.core.products.app.get_active_account", return_value=expected_account)

    result = runner.invoke(
        app,
        ["sync", "--force-create", str(new_product_file)],
        input="y\n",
    )

    assert result.exit_code == 0, result.stdout
    assert "Do you want to create new?" in result.stdout
    assert "Product Sync" in result.stdout


def test_sync_product_no_product(mocker, expected_account, mock_sync_product, new_product_file):
    mocker.patch("swo.mpt.cli.core.products.app.check_product_exists", return_value=None)
    mocker.patch("swo.mpt.cli.core.products.app.get_active_account", return_value=expected_account)

    result = runner.invoke(
        app,
        ["sync", str(new_product_file)],
        input="y\n",
    )

    assert result.exit_code == 0, result.stdout
    assert "Do you want to create new product for account" in result.stdout
    assert "Product Sync" in result.stdout
