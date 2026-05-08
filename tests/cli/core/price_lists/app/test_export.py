import re

from cli.core.price_lists import app
from cli.core.price_lists.services import ItemService, PriceListService
from cli.core.services.service_result import ServiceResult
from cli.core.stats import PriceListStatsCollector
from typer.testing import CliRunner

runner = CliRunner()


def strip_ansi(text):
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def test_export_file_exists(mocker, active_operations_account):
    mocker.patch(
        "cli.core.price_lists.app.export.get_active_account",
        return_value=active_operations_account,
    )
    mocker.patch("pathlib.Path.exists", return_value=True)
    price_list_service_export_spy = mocker.spy(PriceListService, "export")
    item_service_export_spy = mocker.spy(ItemService, "export")

    result = runner.invoke(app, ["export", "PRC-1234-1234-1234"], input="n\n")

    assert result.exit_code == 0
    assert "Skipped export for PRC-1234-1234-1234." in strip_ansi(result.stdout)
    price_list_service_export_spy.assert_not_called()
    item_service_export_spy.assert_not_called()


def test_export_file_exists_overwrite(mocker, active_operations_account, price_list_data_from_json):
    mocker.patch(
        "cli.core.price_lists.app.export.get_active_account",
        return_value=active_operations_account,
    )
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("pathlib.Path.unlink")
    replace_mock = mocker.patch("pathlib.Path.replace")
    stats = PriceListStatsCollector()
    price_list_service_export_mock = mocker.patch(
        "cli.core.price_lists.services.PriceListService.export",
        return_value=ServiceResult(success=True, model=price_list_data_from_json, stats=stats),
    )
    item_service_export_mock = mocker.patch(
        "cli.core.price_lists.services.ItemService.export",
        return_value=ServiceResult(success=True, model=None, stats=stats),
    )

    result = runner.invoke(app, ["export", "PRC-1234-1234-1234"], input="y\n")

    assert result.exit_code == 0, result.stdout
    replace_mock.assert_called_once()
    price_list_service_export_mock.assert_called_once()
    item_service_export_mock.assert_called_once()


def test_export_price_list(mocker, active_operations_account, price_list_data_from_json):
    mocker.patch(
        "cli.core.price_lists.app.export.get_active_account",
        return_value=active_operations_account,
    )
    mocker.patch("pathlib.Path.unlink")
    replace_mock = mocker.patch("pathlib.Path.replace")
    stats = PriceListStatsCollector()
    price_list_service_export_mock = mocker.patch(
        "cli.core.price_lists.services.PriceListService.export",
        return_value=ServiceResult(success=True, model=price_list_data_from_json, stats=stats),
    )
    item_service_export_mock = mocker.patch(
        "cli.core.price_lists.services.ItemService.export",
        return_value=ServiceResult(success=True, model=None, stats=stats),
    )

    result = runner.invoke(app, ["export", "PRC-1234-1234-1234"], input="y\n")

    assert result.exit_code == 0
    assert "Price list with id: PRC-1234-1234-1234 has been exported into" in strip_ansi(
        result.stdout
    )
    replace_mock.assert_called_once()
    price_list_service_export_mock.assert_called_once()
    item_service_export_mock.assert_called_once()


def test_export_price_list_item_no_success(
    mocker, active_operations_account, price_list_data_from_json
):
    mocker.patch(
        "cli.core.price_lists.app.export.get_active_account",
        return_value=active_operations_account,
    )
    stats = PriceListStatsCollector()
    price_list_service_export_mock = mocker.patch(
        "cli.core.price_lists.services.PriceListService.export",
        return_value=ServiceResult(success=True, model=price_list_data_from_json, stats=stats),
    )
    item_service_export_mock = mocker.patch(
        "cli.core.price_lists.services.ItemService.export",
        return_value=ServiceResult(success=False, model=None, stats=stats),
    )

    result = runner.invoke(app, ["export", "PRC-1234-1234-1234"], input="y\n")

    assert result.exit_code == 4
    assert "Price list export FAILED" in strip_ansi(result.stdout)
    price_list_service_export_mock.assert_called_once()
    item_service_export_mock.assert_called_once()


def test_export_price_list_no_operations_account(
    mocker, active_vendor_account, price_list_data_from_json
):
    mocker.patch(
        "cli.core.price_lists.app.export.get_active_account",
        return_value=active_vendor_account,
        autospec=True,
    )
    price_list_service_export_spy = mocker.spy(PriceListService, "export")
    item_service_export_spy = mocker.spy(ItemService, "export")

    result = runner.invoke(app, ["export", "PRC-1234-1234-1234"], input="y\n")

    assert result.exit_code == 4
    assert "Please, activate an operation account." in strip_ansi(result.stdout)
    price_list_service_export_spy.assert_not_called()
    item_service_export_spy.assert_not_called()


def test_export_price_list_no_success(mocker, active_operations_account):
    mocker.patch(
        "cli.core.price_lists.app.export.get_active_account",
        return_value=active_operations_account,
    )
    stats = PriceListStatsCollector()
    price_list_service_export_mock = mocker.patch(
        "cli.core.price_lists.services.PriceListService.export",
        return_value=ServiceResult(success=False, model=None, stats=stats),
    )
    item_service_export_spy = mocker.spy(ItemService, "export")

    result = runner.invoke(app, ["export", "PRC-1234-1234-1234"], input="y\n")

    assert result.exit_code == 4
    assert "Price list export FAILED" in strip_ansi(result.stdout)
    price_list_service_export_mock.assert_called_once()
    item_service_export_spy.assert_not_called()
