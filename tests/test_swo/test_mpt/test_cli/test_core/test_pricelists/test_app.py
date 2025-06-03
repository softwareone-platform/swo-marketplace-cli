from swo.mpt.cli.core.pricelists import app
from swo.mpt.cli.core.pricelists.services import ItemService, PriceListService
from swo.mpt.cli.core.services.service_result import ServiceResult
from swo.mpt.cli.core.stats import PricelistStatsCollector
from typer.testing import CliRunner

runner = CliRunner()


def test_sync_pricelists_not_files_found(pricelist_new_file):
    result = runner.invoke(app, ["sync", "some-file.xlsx"])

    assert result.exit_code == 3, result.stdout
    assert "No files found for provided paths" in result.stdout


def test_sync_pricelists_multiple_files(
    mocker, price_list_data_from_json, pricelist_new_file, expected_account
):
    mocker.patch(
        "swo.mpt.cli.core.pricelists.app.get_active_account", return_value=expected_account
    )
    mocker.patch(
        "swo.mpt.cli.core.pricelists.app.get_files_path",
        return_value=[pricelist_new_file, pricelist_new_file],
    )
    stats = PricelistStatsCollector()
    pricelist_service_retrieve_mock = mocker.patch.object(
        PriceListService,
        "retrieve",
        return_value=ServiceResult(success=True, model=None, stats=stats),
    )
    pricelist_service_create_mock = mocker.patch.object(
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
    assert pricelist_service_retrieve_mock.call_count == 2
    assert pricelist_service_create_mock.call_count == 2
    assert item_service_update_mock.call_count == 2


def test_sync_pricelists_create(
    mocker, mpt_price_list_data, price_list_data_from_json, pricelist_file_path, expected_account
):
    mocker.patch(
        "swo.mpt.cli.core.pricelists.app.get_active_account", return_value=expected_account
    )
    stats = PricelistStatsCollector()
    pricelist_service_retrieve_mock = mocker.patch.object(
        PriceListService,
        "retrieve",
        return_value=ServiceResult(success=True, model=None, stats=stats),
    )
    pricelist_service_create_mock = mocker.patch.object(
        PriceListService,
        "create",
        return_value=ServiceResult(success=True, model=price_list_data_from_json, stats=stats),
    )
    item_service_update_mock = mocker.patch.object(
        ItemService,
        "update",
        return_value=ServiceResult(success=True, model=None, stats=stats),
    )
    pricelist_service_update_spy = mocker.spy(PriceListService, "update")

    result = runner.invoke(app, ["sync", str(pricelist_file_path)], input="y\ny\n")

    assert result.exit_code == 0, result.stdout
    pricelist_service_retrieve_mock.assert_called_once()
    pricelist_service_create_mock.assert_called_once()
    item_service_update_mock.assert_called_once()
    pricelist_service_update_spy.assert_not_called()


def test_sync_pricelists_update(
    mocker, price_list_data_from_json, pricelist_file_path, expected_account
):
    stats = PricelistStatsCollector()
    mocker.patch(
        "swo.mpt.cli.core.pricelists.app.get_active_account", return_value=expected_account
    )
    pricelist_service_retrieve_mock = mocker.patch.object(
        PriceListService,
        "retrieve",
        return_value=ServiceResult(success=True, model=price_list_data_from_json, stats=stats),
    )
    pricelist_service_update_mock = mocker.patch.object(
        PriceListService,
        "update",
        return_value=ServiceResult(success=True, model=price_list_data_from_json, stats=stats),
    )
    item_service_update_mock = mocker.patch.object(
        ItemService,
        "update",
        return_value=ServiceResult(success=True, model=None, stats=stats),
    )
    pricelist_service_create_spy = mocker.spy(PriceListService, "create")

    result = runner.invoke(app, ["sync", str(pricelist_file_path)], input="y\ny\n")

    assert result.exit_code == 0, result.stdout
    pricelist_service_retrieve_mock.assert_called_once()
    pricelist_service_update_mock.assert_called_once_with(price_list_data_from_json.id)
    item_service_update_mock.assert_called_once()
    pricelist_service_create_spy.assert_not_called()


def test_sync_pricelists_create_error(
    mocker, price_list_data_from_json, pricelist_file_path, expected_account
):
    mocker.patch(
        "swo.mpt.cli.core.pricelists.app.get_active_account", return_value=expected_account
    )
    stats = PricelistStatsCollector()
    pricelist_service_retrieve_mock = mocker.patch.object(
        PriceListService,
        "retrieve",
        return_value=ServiceResult(success=True, model=None, stats=stats),
    )
    pricelist_service_create_mock = mocker.patch.object(
        PriceListService,
        "create",
        return_value=ServiceResult(success=False, model=None, stats=stats),
    )
    item_service_update_spy = mocker.spy(ItemService, "update")

    result = runner.invoke(app, ["sync", str(pricelist_file_path)], input="y\ny\n")

    assert result.exit_code == 4
    assert "Pricelist sync FAILED\n" in result.stdout
    pricelist_service_retrieve_mock.assert_called_once()
    pricelist_service_create_mock.assert_called_once()
    item_service_update_spy.assert_not_called()
