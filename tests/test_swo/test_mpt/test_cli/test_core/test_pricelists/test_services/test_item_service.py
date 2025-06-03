from unittest.mock import Mock

import pytest
from requests import Response
from swo.mpt.cli.core.errors import MPTAPIError
from swo.mpt.cli.core.pricelists.api import PriceListItemAPIService
from swo.mpt.cli.core.pricelists.constants import TAB_PRICE_ITEMS
from swo.mpt.cli.core.pricelists.handlers import PriceListItemExcelFileHandler
from swo.mpt.cli.core.pricelists.models import ItemData
from swo.mpt.cli.core.pricelists.services import ItemService
from swo.mpt.cli.core.services.service_context import ServiceContext
from swo.mpt.cli.core.stats import PricelistStatsCollector


@pytest.fixture
def service_context(mpt_client, pricelist_file_path, active_vendor_account, pricelist_item):
    stats = PricelistStatsCollector()
    return ServiceContext(
        account=active_vendor_account,
        api=PriceListItemAPIService(mpt_client, pricelist_item.id),
        data_model=ItemData,
        file_handler=PriceListItemExcelFileHandler(pricelist_file_path),
        stats=stats,
    )


def test_retrieve_from_mpt(mocker, service_context, mpt_item_data, item_data_from_json):
    api_get_mock = mocker.patch.object(
        service_context.api,
        "get",
        return_value=Mock(spec=Response, json=Mock(return_value=mpt_item_data)),
    )
    service = ItemService(service_context)

    result = service.retrieve_from_mpt(item_data_from_json.id)

    assert result.success is True
    assert result.model == item_data_from_json
    api_get_mock.assert_called_once_with(item_data_from_json.id)


def test_retrieve_from_mpt_error(mocker, service_context):
    api_get_mock = mocker.patch.object(
        service_context.api,
        "get",
        side_effect=MPTAPIError("API Error", "Error retrieving item"),
    )
    service = ItemService(service_context)

    result = service.retrieve_from_mpt("fake_id")

    assert result.success is False
    assert len(result.errors) > 0
    assert result.model is None
    api_get_mock.assert_called_once_with("fake_id")


def test_update_item(mocker, service_context, mpt_item_data, item_data_from_dict):
    mocker.patch.object(item_data_from_dict, "to_update", return_value=True)
    mocker.patch.object(
        service_context.file_handler, "read_items_data", return_value=[item_data_from_dict]
    )
    mocker.patch.object(service_context.api, "list", return_value=[mpt_item_data])
    file_handler_write_mock = mocker.patch.object(service_context.file_handler, "write_id")
    update_mock = mocker.patch.object(service_context.api, "update", return_value=mpt_item_data)
    stats_spy = mocker.spy(service_context.stats, "add_synced")
    service = ItemService(service_context)

    result = service.update(item_data_from_dict.id)

    assert result.success is True
    assert result.model is None
    assert service_context.stats.tabs["Price Items"]["synced"] == 1
    update_mock.assert_called_once()
    file_handler_write_mock.assert_called_once_with(
        item_data_from_dict.coordinate, item_data_from_dict.id
    )
    stats_spy.assert_called_once_with(TAB_PRICE_ITEMS)


def test_update_item_error(mocker, service_context):
    mocker.patch.object(
        service_context.api,
        "exists",
        side_effect=MPTAPIError("API Error", "Error retrieving item"),
    )
    file_handler_mock = mocker.patch.object(service_context.file_handler, "write_error")
    api_update_spy = mocker.spy(service_context.api, "update")
    stats_add_synced_spy = mocker.spy(service_context.stats, "add_synced")
    service = ItemService(service_context)

    result = service.update("fake_id")

    assert result.success is False
    assert len(result.errors) > 0
    assert result.model is None
    api_update_spy.assert_not_called()
    file_handler_mock.assert_called()
    stats_add_synced_spy.assert_not_called()


def test_update_item_not_found(mocker, service_context):
    mocker.patch.object(service_context.api, "exists", return_value=False)
    file_handler_mock = mocker.patch.object(service_context.file_handler, "write_error")
    stats_spy = mocker.spy(service_context.stats, "add_error")
    service = ItemService(service_context)

    result = service.update("fake-id")

    assert not result.success
    assert len(result.errors) > 0
    assert result.model is None
    file_handler_mock.assert_called()
    stats_spy.assert_called()


def test_update_item_skip(mocker, service_context, mpt_item_data, item_data_from_json):
    mocker.patch.object(
        service_context.file_handler, "read_items_data", return_value=[item_data_from_json]
    )
    mocker.patch.object(item_data_from_json, "to_update", return_value=False)
    file_handler_write_mock = mocker.patch.object(service_context.file_handler, "write_id")
    api_update_spy = mocker.spy(service_context.api, "update")
    stats_spy = mocker.spy(service_context.stats, "add_skipped")
    service = ItemService(service_context)

    result = service.update(item_data_from_json.id)

    assert result.success is True
    file_handler_write_mock.assert_not_called()
    api_update_spy.assert_not_called()
    stats_spy.assert_called_once_with(TAB_PRICE_ITEMS)
