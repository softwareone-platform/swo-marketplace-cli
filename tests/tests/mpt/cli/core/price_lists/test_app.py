from swo.mpt.cli.core.price_lists import app
from swo.mpt.cli.core.price_lists.services import ItemService, PriceListService
from swo.mpt.cli.core.services.service_result import ServiceResult
from swo.mpt.cli.core.stats import PriceListStatsCollector
from typer.testing import CliRunner

runner = CliRunner()


def test_sync_price_lists_not_files_found(price_list_new_file):
    result = runner.invoke(app, ["sync", "some-file.xlsx"])

    assert result.exit_code == 3, result.stdout
    assert "No files found for provided paths" in result.stdout


def test_sync_price_lists_multiple_files(
    mocker, price_list_data_from_json, price_list_new_file, expected_account
):
    mocker.patch(
        "swo.mpt.cli.core.price_lists.app.get_active_account", return_value=expected_account
    )
    mocker.patch(
        "swo.mpt.cli.core.price_lists.app.get_files_path",
        return_value=[price_list_new_file, price_list_new_file],
    )
    stats = PriceListStatsCollector()
    price_list_service_retrieve_mock = mocker.patch.object(
        PriceListService,
        "retrieve",
        return_value=ServiceResult(success=True, model=None, stats=stats),
    )
    price_list_service_create_mock = mocker.patch.object(
        PriceListService,
        "create",
        return_value=ServiceResult(success=True, model=price_list_data_from_json, stats=stats),
    )
    item_service_update_mock = mocker.patch.object(
        ItemService,
        "update",
        return_value=ServiceResult(success=True, model=None, stats=stats),
    )

    result = runner.invoke(
        app,
        ["sync", "fake_dir_path"],
        input="y\ny\ny\ny\n",
    )
    assert result.exit_code == 0, result.stdout
    assert price_list_service_retrieve_mock.call_count == 2
    assert price_list_service_create_mock.call_count == 2
    assert item_service_update_mock.call_count == 2


def test_sync_price_lists_create(
    mocker, mpt_price_list_data, price_list_data_from_json, price_list_file_path, expected_account
):
    mocker.patch(
        "swo.mpt.cli.core.price_lists.app.get_active_account", return_value=expected_account
    )
    stats = PriceListStatsCollector()
    price_list_service_retrieve_mock = mocker.patch.object(
        PriceListService,
        "retrieve",
        return_value=ServiceResult(success=True, model=None, stats=stats),
    )
    price_list_service_create_mock = mocker.patch.object(
        PriceListService,
        "create",
        return_value=ServiceResult(success=True, model=price_list_data_from_json, stats=stats),
    )
    item_service_update_mock = mocker.patch.object(
        ItemService,
        "update",
        return_value=ServiceResult(success=True, model=None, stats=stats),
    )
    price_list_service_update_spy = mocker.spy(PriceListService, "update")

    result = runner.invoke(app, ["sync", str(price_list_file_path)], input="y\ny\n")

    assert result.exit_code == 0, result.stdout
    price_list_service_retrieve_mock.assert_called_once()
    price_list_service_create_mock.assert_called_once()
    item_service_update_mock.assert_called_once()
    price_list_service_update_spy.assert_not_called()


def test_sync_price_lists_update(
    mocker, price_list_data_from_json, price_list_file_path, expected_account
):
    stats = PriceListStatsCollector()
    mocker.patch(
        "swo.mpt.cli.core.price_lists.app.get_active_account", return_value=expected_account
    )
    price_list_service_retrieve_mock = mocker.patch.object(
        PriceListService,
        "retrieve",
        return_value=ServiceResult(success=True, model=price_list_data_from_json, stats=stats),
    )
    price_list_service_update_mock = mocker.patch.object(
        PriceListService,
        "update",
        return_value=ServiceResult(success=True, model=price_list_data_from_json, stats=stats),
    )
    item_service_update_mock = mocker.patch.object(
        ItemService,
        "update",
        return_value=ServiceResult(success=True, model=None, stats=stats),
    )
    price_list_service_create_spy = mocker.spy(PriceListService, "create")

    result = runner.invoke(app, ["sync", str(price_list_file_path)], input="y\ny\n")

    assert result.exit_code == 0, result.stdout
    price_list_service_retrieve_mock.assert_called_once()
    price_list_service_update_mock.assert_called_once_with()
    item_service_update_mock.assert_called_once()
    price_list_service_create_spy.assert_not_called()


def test_sync_price_lists_create_error(
    mocker, active_operations_account, price_list_data_from_json, price_list_file_path
):
    mocker.patch(
        "swo.mpt.cli.core.price_lists.app.get_active_account",
        return_value=active_operations_account,
    )
    stats = PriceListStatsCollector()
    price_list_service_retrieve_mock = mocker.patch.object(
        PriceListService,
        "retrieve",
        return_value=ServiceResult(success=True, model=None, stats=stats),
    )
    price_list_service_create_mock = mocker.patch.object(
        PriceListService,
        "create",
        return_value=ServiceResult(success=False, model=None, stats=stats),
    )
    item_service_update_spy = mocker.spy(ItemService, "update")

    result = runner.invoke(app, ["sync", str(price_list_file_path)], input="y\ny\n")

    assert result.exit_code == 4
    assert "Price list sync FAILED\n" in result.stdout
    price_list_service_retrieve_mock.assert_called_once()
    price_list_service_create_mock.assert_called_once()
    item_service_update_spy.assert_not_called()


def test_export_price_list(mocker, active_operations_account, price_list_data_from_json):
    mocker.patch(
        "swo.mpt.cli.core.price_lists.app.get_active_account",
        return_value=active_operations_account,
    )
    stats = PriceListStatsCollector()
    price_list_service_export_mock = mocker.patch(
        "swo.mpt.cli.core.price_lists.services.PriceListService.export",
        return_value=ServiceResult(success=True, model=price_list_data_from_json, stats=stats),
    )
    item_service_export_mock = mocker.patch(
        "swo.mpt.cli.core.price_lists.services.ItemService.export",
        return_value=ServiceResult(success=True, model=None, stats=stats),
    )

    result = runner.invoke(app, ["export", "PRC-1234-1234-1234"], input="y\n")

    assert result.exit_code == 0
    assert "Price list with id: PRC-1234-1234-1234 has been exported into" in result.stdout
    price_list_service_export_mock.assert_called_once()
    item_service_export_mock.assert_called_once()


def test_export_file_exists(mocker, active_operations_account):
    mocker.patch(
        "swo.mpt.cli.core.price_lists.app.get_active_account",
        return_value=active_operations_account,
    )
    mocker.patch("pathlib.Path.exists", return_value=True)
    price_list_service_export_spy = mocker.spy(PriceListService, "export")
    item_service_export_spy = mocker.spy(ItemService, "export")

    result = runner.invoke(app, ["export", "PRC-1234-1234-1234"], input="n\n")

    assert result.exit_code == 0
    assert "Skipped export for PRC-1234-1234-1234." in result.stdout
    price_list_service_export_spy.assert_not_called()
    item_service_export_spy.assert_not_called()


def test_export_price_list_no_operations_account(
    mocker, active_vendor_account, price_list_data_from_json
):
    mocker.patch(
        "swo.mpt.cli.core.price_lists.app.get_active_account", return_value=active_vendor_account
    )
    price_list_service_export_spy = mocker.spy(PriceListService, "export")
    item_service_export_spy = mocker.spy(ItemService, "export")

    result = runner.invoke(app, ["export", "PRC-1234-1234-1234"], input="y\n")

    assert result.exit_code == 4
    assert "Please, activate an operation account." in result.stdout
    price_list_service_export_spy.assert_not_called()
    item_service_export_spy.assert_not_called()


def test_export_price_list_export_price_list_no_success(
    mocker, active_operations_account, price_list_data_from_json
):
    mocker.patch(
        "swo.mpt.cli.core.price_lists.app.get_active_account",
        return_value=active_operations_account,
    )
    stats = PriceListStatsCollector()
    price_list_service_export_mock = mocker.patch(
        "swo.mpt.cli.core.price_lists.services.PriceListService.export",
        return_value=ServiceResult(success=False, model=None, stats=stats),
    )
    item_service_export_spy = mocker.spy(ItemService, "export")

    result = runner.invoke(app, ["export", "PRC-1234-1234-1234"], input="y\n")

    assert result.exit_code == 4
    assert "Price list export FAILED" in result.stdout
    price_list_service_export_mock.assert_called_once()
    item_service_export_spy.assert_not_called()


def test_export_price_list_item_no_success(
    mocker, active_operations_account, price_list_data_from_json
):
    mocker.patch(
        "swo.mpt.cli.core.price_lists.app.get_active_account",
        return_value=active_operations_account,
    )
    stats = PriceListStatsCollector()
    price_list_service_export_mock = mocker.patch(
        "swo.mpt.cli.core.price_lists.services.PriceListService.export",
        return_value=ServiceResult(success=True, model=price_list_data_from_json, stats=stats),
    )
    item_service_export_mock = mocker.patch(
        "swo.mpt.cli.core.price_lists.services.ItemService.export",
        return_value=ServiceResult(success=False, model=None, stats=stats),
    )

    result = runner.invoke(app, ["export", "PRC-1234-1234-1234"], input="y\n")

    assert result.exit_code == 4
    assert "Price list export FAILED" in result.stdout
    price_list_service_export_mock.assert_called_once()
    item_service_export_mock.assert_called_once()
