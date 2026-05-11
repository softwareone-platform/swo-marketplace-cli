from pathlib import Path

import pytest
from cli.core.products import app as product_app
from cli.core.stats import ProductStatsCollector
from mpt_api_client.models import Collection, Model, Pagination
from mpt_api_client.models import Meta as ClientMeta
from openpyxl.reader.excel import load_workbook
from typer.testing import CliRunner

runner = CliRunner()


def make_collection(mocker, data_list):
    collection = mocker.MagicMock(spec=Collection)
    collection.meta = mocker.MagicMock(spec=ClientMeta)
    collection.meta.pagination = mocker.MagicMock(spec=Pagination)
    collection.meta.pagination.limit = 100
    collection.meta.pagination.offset = 0
    collection.meta.pagination.total = len(data_list)
    resources = []
    for resource_data in data_list:
        resource = mocker.MagicMock(spec=Model)
        resource.to_dict.return_value = resource_data
        resources.append(resource)
    collection.resources = resources
    return collection


def test_export_skipped_when_user_declines(mocker, product_container_mock):
    mocker.patch("pathlib.Path.exists", return_value=True)

    result = runner.invoke(product_app, ["export", "PRD-1234"], input="n\n")

    assert result.exit_code == 0, result.stdout
    assert "Skipped export for PRD-1234." in result.stdout
    product_container_mock.product_service().export.assert_not_called()


def test_export_product_account_not_allowed(account_container_mock, active_vendor_account):
    account_container_mock.account.override(active_vendor_account)

    result = runner.invoke(product_app, ["export", "fake_id"])

    assert result.exit_code == 4, result.stdout


def test_export_product_error_exporting_product(mocker, product_container_mock):
    product_container_mock.stats.override(mocker.Mock(spec=ProductStatsCollector, has_errors=True))
    mocker.patch("pathlib.Path.unlink")
    mocker.patch("pathlib.Path.replace")

    result = runner.invoke(product_app, ["export", "fake_id"], input="y\n")

    assert result.exit_code == 3, result.stdout


def test_export_product_overwrites_existing_files(
    mocker,
    tmp_path,
    product_container_mock,
):
    exists_mock = mocker.patch.object(Path, "exists", return_value=True)
    unlink_mock = mocker.patch.object(Path, "unlink", return_value=True)
    replace_mock = mocker.patch.object(Path, "replace")
    product_container_mock.stats.override(mocker.Mock(spec=ProductStatsCollector, has_errors=False))
    product_id = "PRD-1234"
    tmp_file = tmp_path / f"{product_id}.xlsx"
    tmp_file.touch()

    result = runner.invoke(
        product_app,
        ["export", product_id, "--out", str(tmp_file)],
        input="y\ny\n",
    )

    assert result.exit_code == 0, result.stdout
    exists_mock.assert_called()
    assert tmp_file.exists()
    unlink_mock.assert_called()
    replace_mock.assert_called_once()
    product_container_mock.product_service().export.assert_called_once()


@pytest.mark.integration
def test_export_product(
    tmp_path,
    mocker,
    account_container_mock,
    mpt_product_data,
    product_related_data,
):
    mock_api_client = account_container_mock.api_mpt_client()
    product_resource = mocker.MagicMock(spec=Model)
    product_resource.to_dict.return_value = mpt_product_data
    mock_api_client.catalog.products.get.return_value = product_resource
    mock_items = mock_api_client.catalog.items
    mock_items_select = mock_items.filter.return_value.select.return_value
    mock_items_select.fetch_page.return_value = make_collection(
        mocker, [product_related_data["mpt_item"]]
    )
    item_groups = mock_api_client.catalog.products.item_groups.return_value
    item_groups.select.return_value.fetch_page.return_value = make_collection(
        mocker, [product_related_data["mpt_item_group"]]
    )
    parameter_groups = mock_api_client.catalog.products.parameter_groups.return_value
    parameter_groups.select.return_value.fetch_page.return_value = make_collection(
        mocker, [product_related_data["mpt_parameter_group"]]
    )
    params_service = mock_api_client.catalog.products.parameters.return_value
    params_service_select = params_service.filter.return_value.select.return_value
    params_service_select.fetch_page.side_effect = [
        make_collection(mocker, [product_related_data["mpt_agreement_parameter"]]),
        make_collection(mocker, [product_related_data["mpt_asset_parameter"]]),
        make_collection(mocker, [product_related_data["mpt_item_parameter"]]),
        make_collection(mocker, [product_related_data["mpt_request_parameter"]]),
        make_collection(mocker, [product_related_data["mpt_subscription_parameter"]]),
    ]
    products_templates = mock_api_client.catalog.products.templates.return_value
    products_templates.select.return_value.fetch_page.return_value = make_collection(
        mocker, [product_related_data["mpt_template"]]
    )
    product_id = "PRD-0232-2541"

    result = runner.invoke(
        product_app, ["export", product_id, "--out", str(tmp_path)], input="y\ny\n"
    )

    assert result.exit_code == 0, result.stdout
    product_path = tmp_path / f"{product_id}.xlsx"
    assert product_path.exists()
    wb = load_workbook(product_path)
    expected_sheets = [
        "General",
        "Settings",
        "Items",
        "Items Groups",
        "Parameters Groups",
        "Agreements Parameters",
        "Assets Parameters",
        "Item Parameters",
        "Request Parameters",
        "Subscription Parameters",
        "Templates",
    ]
    assert wb.sheetnames == expected_sheets
    general_sheet = wb["General"]
    assert general_sheet.max_row == 12
    assert general_sheet["A1"].value == "General Information"
    assert general_sheet["A2"].value == "Product ID"
    assert general_sheet["B2"].value == product_id
    settings_sheet = wb["Settings"]
    assert settings_sheet.max_row == 12
    assert settings_sheet["A1"].value == "Setting"
    assert settings_sheet["A2"].value == "Change order validation (draft)"
    assert settings_sheet["C2"].value == "Enabled"
    items_sheet = wb["Items"]
    assert items_sheet.max_row == 2
    assert items_sheet["A1"].value == "ID"
    assert items_sheet["A2"].value == "ITM-0232-2541-0001"
    items_groups_sheet = wb["Items Groups"]
    assert items_groups_sheet.max_row == 2
    assert items_groups_sheet["A1"].value == "ID"
    assert items_groups_sheet["A2"].value == "IGR-0232-2541-0001"
    parameters_groups_sheet = wb["Parameters Groups"]
    assert parameters_groups_sheet.max_row == 2
    assert parameters_groups_sheet["A1"].value == "ID"
    assert parameters_groups_sheet["A2"].value == "PGR-0232-2541-0002"
    agreements_params_sheet = wb["Agreements Parameters"]
    assert agreements_params_sheet.max_row == 2
    assert agreements_params_sheet["A1"].value == "ID"
    assert agreements_params_sheet["A2"].value == "PAR-0232-2541-0001"
    assets_params_sheet = wb["Assets Parameters"]
    assert assets_params_sheet.max_row == 2
    assert assets_params_sheet["A1"].value == "ID"
    assert assets_params_sheet["A2"].value == "PAR-0232-2541-0027"
    item_params_sheet = wb["Item Parameters"]
    assert item_params_sheet.max_row == 2
    assert item_params_sheet["A1"].value == "ID"
    assert item_params_sheet["A2"].value == "PAR-0232-2541-0022"
    request_params_sheet = wb["Request Parameters"]
    assert request_params_sheet.max_row == 2
    assert request_params_sheet["A1"].value == "ID"
    assert request_params_sheet["A2"].value == "PAR-0232-2541-0012"
    subscription_parameter_sheet = wb["Subscription Parameters"]
    assert subscription_parameter_sheet.max_row == 2
    assert subscription_parameter_sheet["A1"].value == "ID"
    assert subscription_parameter_sheet["A2"].value == "PAR-0232-2541-0023"
    templates_sheet = wb["Templates"]
    assert templates_sheet.max_row == 2
    assert templates_sheet["A1"].value == "ID"
    assert templates_sheet["A2"].value == "TPL-0232-2541-0005"
    wb.close()
