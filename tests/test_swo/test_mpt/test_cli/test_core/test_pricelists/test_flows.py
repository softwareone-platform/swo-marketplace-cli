from pathlib import Path
from unittest import mock

from swo.mpt.cli.core.console import console
from swo.mpt.cli.core.errors import MPTAPIError
from swo.mpt.cli.core.handlers.excel_file_handler import ExcelFileHandler
from swo.mpt.cli.core.pricelists import constants
from swo.mpt.cli.core.pricelists.flows import (
    PricelistAction,
    check_pricelist,
    sync_pricelist,
    sync_pricelist_items,
)
from swo.mpt.cli.core.stats import PricelistStatsCollector


def test_check_pricelist(mocker, mpt_client, pricelist_new_file, pricelist):
    mocked_get_pricelist = mocker.patch(
        "swo.mpt.cli.core.pricelists.flows.get_pricelist", return_value=pricelist
    )

    returned_pricelist = check_pricelist(mpt_client, pricelist_new_file)

    assert returned_pricelist == pricelist
    mocked_get_pricelist.assert_called_once_with(mpt_client, "PRC-0232-2541-0003")


def test_check_pricelist_not_found(mocker, mpt_client, pricelist_new_file, pricelist):
    mocked_get_pricelist = mocker.patch(
        "swo.mpt.cli.core.pricelists.flows.get_pricelist",
        side_effect=MPTAPIError("not found", "not found"),
    )

    returned_pricelist = check_pricelist(mpt_client, pricelist_new_file)

    assert not returned_pricelist
    mocked_get_pricelist.assert_called_once_with(mpt_client, "PRC-0232-2541-0003")


def test_sync_pricelist_create_vendor(
    mocker, mpt_client, pricelist, pricelist_new_file, active_vendor_account
):
    stats = PricelistStatsCollector()

    create_mock = mocker.patch(
        "swo.mpt.cli.core.pricelists.flows.create_pricelist", return_value=pricelist
    )
    sync_items_mock = mocker.patch(
        "swo.mpt.cli.core.pricelists.flows.sync_pricelist_items", return_value=stats
    )

    returned_stats, returned_pricelist = sync_pricelist(
        mpt_client,
        pricelist_new_file,
        PricelistAction.CREATE,
        active_vendor_account,
        stats,
        console,
    )

    assert returned_stats.tabs[constants.TAB_GENERAL]["synced"] == 1
    file_handler = ExcelFileHandler(pricelist_new_file)
    assert file_handler.get_cell_value_by_coordinate(constants.TAB_GENERAL, "B3") == pricelist.id
    assert returned_pricelist == pricelist
    create_mock.assert_called_once_with(
        mpt_client,
        {
            "currency": "EUR",
            "precision": 2,
            "notes": "Note 1",
            "product": {
                "id": "PRD-0232-2541",
            },
        },
    )
    sync_items_mock.assert_called_once_with(
        mpt_client,
        mock.ANY,  # TODO: it should be an excel_file_handler_mock
        pricelist.id,
        active_vendor_account,
        stats,
        console,
    )


def test_sync_pricelist_create_operations(
    mocker, mpt_client, pricelist, pricelist_new_file, active_operations_account
):
    stats = PricelistStatsCollector()

    create_mock = mocker.patch(
        "swo.mpt.cli.core.pricelists.flows.create_pricelist", return_value=pricelist
    )
    sync_items_mock = mocker.patch(
        "swo.mpt.cli.core.pricelists.flows.sync_pricelist_items", return_value=stats
    )

    returned_stats, returned_pricelist = sync_pricelist(
        mpt_client,
        pricelist_new_file,
        PricelistAction.CREATE,
        active_operations_account,
        stats,
        console,
    )

    assert returned_stats.tabs[constants.TAB_GENERAL]["synced"] == 1
    file_handler = ExcelFileHandler(pricelist_new_file)
    assert file_handler.get_cell_value_by_coordinate(constants.TAB_GENERAL, "B3") == pricelist.id
    assert returned_pricelist == pricelist
    create_mock.assert_called_once_with(
        mpt_client,
        {
            "currency": "EUR",
            "precision": 2,
            "notes": "Note 1",
            "product": {
                "id": "PRD-0232-2541",
            },
            "defaultMarkup": 10.00,
        },
    )
    sync_items_mock.assert_called_once_with(
        mpt_client,
        mock.ANY,  # TODO: it should be an excel_file_handler_mock
        pricelist.id,
        active_operations_account,
        stats,
        console,
    )


def test_sync_pricelist_update_vendor(
    mocker, mpt_client, pricelist, pricelist_new_file, active_vendor_account
):
    stats = PricelistStatsCollector()

    update_mock = mocker.patch(
        "swo.mpt.cli.core.pricelists.flows.update_pricelist", return_value=pricelist
    )
    sync_items_mock = mocker.patch(
        "swo.mpt.cli.core.pricelists.flows.sync_pricelist_items", return_value=stats
    )

    returned_stats, returned_pricelist = sync_pricelist(
        mpt_client,
        Path(pricelist_new_file),
        PricelistAction.UPDATE,
        active_vendor_account,
        stats,
        console,
    )

    assert returned_stats.tabs[constants.TAB_GENERAL]["synced"] == 1
    assert returned_pricelist == pricelist
    update_mock.assert_called_once_with(
        mpt_client,
        "PRC-0232-2541-0003",
        {
            "currency": "EUR",
            "precision": 2,
            "notes": "Note 1",
            "product": {
                "id": "PRD-0232-2541",
            },
        },
    )
    sync_items_mock.assert_called_once_with(
        mpt_client,
        mock.ANY,  # TODO: it should be an excel_file_handler_mock
        pricelist.id,
        active_vendor_account,
        stats,
        console,
    )


def test_sync_pricelist_update_operations(
    mocker, mpt_client, pricelist, pricelist_new_file, active_operations_account
):
    stats = PricelistStatsCollector()

    update_mock = mocker.patch(
        "swo.mpt.cli.core.pricelists.flows.update_pricelist", return_value=pricelist
    )
    sync_items_mock = mocker.patch(
        "swo.mpt.cli.core.pricelists.flows.sync_pricelist_items", return_value=stats
    )

    returned_stats, returned_pricelist = sync_pricelist(
        mpt_client,
        pricelist_new_file,
        PricelistAction.UPDATE,
        active_operations_account,
        stats,
        console,
    )

    assert returned_stats.tabs[constants.TAB_GENERAL]["synced"] == 1
    file_handler = ExcelFileHandler(pricelist_new_file)
    assert file_handler.get_cell_value_by_coordinate(constants.TAB_GENERAL, "B3") == pricelist.id
    assert returned_pricelist == pricelist
    update_mock.assert_called_once_with(
        mpt_client,
        "PRC-0232-2541-0003",
        {
            "currency": "EUR",
            "precision": 2,
            "notes": "Note 1",
            "product": {
                "id": "PRD-0232-2541",
            },
            "defaultMarkup": 10.00,
        },
    )
    sync_items_mock.assert_called_once_with(
        mpt_client,
        mock.ANY,  # TODO: it should be an excel_file_handler_mock
        pricelist.id,
        active_operations_account,
        stats,
        console,
    )


def test_sync_pricelist_items_vendor(
    mocker,
    mpt_client,
    pricelist_item,
    pricelist_new_file,
    active_vendor_account,
):
    stats = PricelistStatsCollector()
    update_mock = mocker.patch(
        "swo.mpt.cli.core.pricelists.flows.update_pricelist_item", return_value=pricelist_item
    )
    mocker.patch(
        "swo.mpt.cli.core.pricelists.flows.get_pricelist_item", return_value=pricelist_item
    )

    returned_stats = sync_pricelist_items(
        mpt_client,
        pricelist_new_file,
        "PRC-1234-1234",
        active_vendor_account,
        stats,
        console,
    )

    assert returned_stats.tabs[constants.TAB_PRICE_ITEMS]["synced"] == 3
    assert returned_stats.tabs[constants.TAB_PRICE_ITEMS]["skipped"] == 1
    assert update_mock.call_count == 3
    assert update_mock.mock_calls[0].args == (
        mpt_client,
        "PRC-1234-1234",
        pricelist_item.id,
        {
            "status": "ForSale",
            "unitLP": 10.28,
            "unitPP": 12.3,
        },
    )


def test_sync_pricelist_items_operations(
    mocker,
    mpt_client,
    pricelist_item,
    pricelist_new_file,
    active_operations_account,
):
    stats = PricelistStatsCollector()
    update_mock = mocker.patch(
        "swo.mpt.cli.core.pricelists.flows.update_pricelist_item", return_value=pricelist_item
    )
    mocker.patch(
        "swo.mpt.cli.core.pricelists.flows.get_pricelist_item", return_value=pricelist_item
    )

    returned_stats = sync_pricelist_items(
        mpt_client,
        pricelist_new_file,
        "PRC-1234-1234",
        active_operations_account,
        stats,
        console,
    )

    assert returned_stats.tabs[constants.TAB_PRICE_ITEMS]["synced"] == 3
    assert returned_stats.tabs[constants.TAB_PRICE_ITEMS]["skipped"] == 1
    assert update_mock.call_count == 3
    assert update_mock.mock_calls[0].args == (
        mpt_client,
        "PRC-1234-1234",
        pricelist_item.id,
        {
            "markup": 0.10,
            "unitSP": 12.55,
            "unitLP": 10.28,
            "unitPP": 12.3,
            "status": "ForSale",
        },
    )
    assert update_mock.mock_calls[2].args == (
        mpt_client,
        "PRC-1234-1234",
        pricelist_item.id,
        {
            "markup": 0.30,
            "unitLP": 10.28,
            "unitPP": 12.3,
        },
    )


def test_sync_pricelist_create_vendor_external_id(
    mocker, mpt_client, pricelist, pricelist_new_file, active_vendor_account
):
    stats = PricelistStatsCollector()
    file_handler = ExcelFileHandler(pricelist_new_file)
    file_handler.write(
        [
            {constants.TAB_GENERAL: {"A16": "External ID"}},
            {constants.TAB_GENERAL: {"B16": "my_external_id"}},
        ]
    )
    create_mock = mocker.patch(
        "swo.mpt.cli.core.pricelists.flows.create_pricelist", return_value=pricelist
    )
    sync_items_mock = mocker.patch(
        "swo.mpt.cli.core.pricelists.flows.sync_pricelist_items", return_value=stats
    )

    returned_stats, returned_pricelist = sync_pricelist(
        mpt_client,
        pricelist_new_file,
        PricelistAction.CREATE,
        active_vendor_account,
        stats,
        console,
    )

    assert returned_stats.tabs[constants.TAB_GENERAL]["synced"] == 1
    file_handler = ExcelFileHandler(pricelist_new_file)
    assert file_handler.get_cell_value_by_coordinate(constants.TAB_GENERAL, "B3") == pricelist.id
    assert returned_pricelist == pricelist
    create_mock.assert_called_once_with(
        mpt_client,
        {
            "currency": "EUR",
            "externalIds": {"vendor": "my_external_id"},
            "precision": 2,
            "notes": "Note 1",
            "product": {
                "id": "PRD-0232-2541",
            },
        },
    )
    sync_items_mock.assert_called_once_with(
        mpt_client,
        mock.ANY,  # TODO: it should be an excel_file_handler_mock
        pricelist.id,
        active_vendor_account,
        stats,
        console,
    )
