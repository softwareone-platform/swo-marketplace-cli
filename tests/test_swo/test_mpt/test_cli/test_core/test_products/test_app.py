import json
from urllib.parse import urljoin

from swo.mpt.cli.core.products import app
from typer.testing import CliRunner

runner = CliRunner()


def test_list_products_account_file_not_exists(tmp_path, mocker):
    account_file_path = tmp_path / ".swocli" / "accounts.json"
    mocker.patch(
        "swo.mpt.cli.core.products.app.get_accounts_file_path",
        return_value=account_file_path,
    )

    result = runner.invoke(app, [])

    assert result.exit_code == 3, result.stdout
    assert "No active account found." in result.stdout


def test_list_products_accounts_not_active(new_accounts_path, mocker):
    with open(new_accounts_path) as f:
        accounts = json.load(f)

    for account in accounts:
        account["is_active"] = False

    with open(new_accounts_path, "w") as f:
        json.dump(accounts, f)

    mocker.patch(
        "swo.mpt.cli.core.products.app.get_accounts_file_path",
        return_value=new_accounts_path,
    )

    result = runner.invoke(app, [])

    assert result.exit_code == 3, result.stdout
    assert "No active account found." in result.stdout


def test_list_products(
    new_accounts_path, mocker, requests_mocker, mpt_client, mpt_products_response
):
    mocker.patch(
        "swo.mpt.cli.core.products.app.get_accounts_file_path",
        return_value=new_accounts_path,
    )
    requests_mocker.get(
        urljoin(
            mpt_client.base_url, "/products?limit=10&offset=0", allow_fragments=True
        ),
        json=mpt_products_response,
    )

    result = runner.invoke(app, [])

    assert result.exit_code == 0, result.stdout
    assert mpt_products_response["data"][0]["id"] in result.stdout


def test_list_products_with_query_and_paging(
    new_accounts_path, mocker, requests_mocker, mpt_client, mpt_products_response
):
    mocker.patch(
        "swo.mpt.cli.core.products.app.get_accounts_file_path",
        return_value=new_accounts_path,
    )
    requests_mocker.get(
        urljoin(
            mpt_client.base_url,
            "/products?limit=20&offset=0&eq(product.id,PRD-1234)",
            allow_fragments=True,
        ),
        json=mpt_products_response,
    )

    result = runner.invoke(
        app,
        ["--page", "20", "--query", "eq(product.id,PRD-1234)"],
    )

    assert result.exit_code == 0, result.stdout
    assert mpt_products_response["data"][0]["id"] in result.stdout
