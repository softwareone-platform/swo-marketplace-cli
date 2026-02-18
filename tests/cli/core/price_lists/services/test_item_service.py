from unittest.mock import Mock

import pytest
from cli.core.errors import MPTAPIError
from cli.core.price_lists.api import PriceListItemAPIService
from cli.core.price_lists.constants import TAB_PRICE_ITEMS
from cli.core.price_lists.handlers import PriceListItemExcelFileManager
from cli.core.price_lists.models import ItemData
from cli.core.price_lists.services import ItemService
from cli.core.services.service_context import ServiceContext
from cli.core.stats import PriceListStatsCollector
from requests import Response


@pytest.fixture
def service_context(mpt_client, price_list_file_path, active_vendor_account, item_data_from_dict):
    stats = PriceListStatsCollector()
    return ServiceContext(
        account=active_vendor_account,
        api=PriceListItemAPIService(mpt_client, item_data_from_dict.id),
        data_model=ItemData,
        file_manager=PriceListItemExcelFileManager(price_list_file_path),
        stats=stats,
    )


def test_export(mocker, service_context, mpt_item_data):
    create_tab_mock = mocker.patch.object(service_context.file_manager, "create_tab")
    add_mock = mocker.patch.object(service_context.file_manager, "add")
    response_data = {"data": [mpt_item_data], "meta": {"offset": 1, "limit": 100, "total": 1}}
    api_list_mock = mocker.patch.object(service_context.api, "list", side_effect=[response_data])

    result = ItemService(service_context).export()

    assert result.success is True
    create_tab_mock.assert_called_once()
    add_mock.assert_called()
    api_list_mock.assert_called()


def test_export_mpt_error(mocker, service_context):
    create_tab_mock = mocker.patch.object(service_context.file_manager, "create_tab")
    api_list_mock = mocker.patch.object(
        service_context.api, "list", side_effect=MPTAPIError("API Error", "Error retrieving item")
    )
    add_spy = mocker.spy(service_context.file_manager, "add")

    result = ItemService(service_context).export()

    assert result.success is False
    create_tab_mock.assert_called_once()
    api_list_mock.assert_called()
    add_spy.assert_not_called()


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
        service_context.file_manager, "read_data", return_value=[item_data_from_dict]
    )
    mocker.patch.object(service_context.api, "list", return_value={"data": [mpt_item_data]})
    write_ids_mock = mocker.patch.object(service_context.file_manager, "write_ids")
    update_mock = mocker.patch.object(service_context.api, "update", return_value=mpt_item_data)
    stats_spy = mocker.spy(service_context.stats, "add_synced")
    service = ItemService(service_context)

    result = service.update()

    assert result.success is True
    assert result.model is None
    assert service_context.stats.tabs["Price Items"]["synced"] == 1
    update_mock.assert_called_once()
    write_ids_mock.assert_called_once_with({item_data_from_dict.coordinate: item_data_from_dict.id})
    stats_spy.assert_called_once_with(TAB_PRICE_ITEMS)


def test_update_item_api_list_error(mocker, service_context):
    mocker.patch.object(
        service_context.api,
        "list",
        side_effect=MPTAPIError("API Error", "Error retrieving item"),
    )
    file_handler_mock = mocker.patch.object(service_context.file_manager, "write_error")
    api_update_spy = mocker.spy(service_context.api, "update")
    stats_add_synced_spy = mocker.spy(service_context.stats, "add_synced")
    service = ItemService(service_context)

    result = service.update()

    assert result.success is False
    assert len(result.errors) > 0
    assert result.model is None
    api_update_spy.assert_not_called()
    file_handler_mock.assert_called()
    stats_add_synced_spy.assert_not_called()


def test_update_item_api_update_error(mocker, service_context, mpt_item_data, item_data_from_dict):
    mocker.patch.object(item_data_from_dict, "to_update", return_value=True)
    mocker.patch.object(
        service_context.file_manager, "read_data", return_value=[item_data_from_dict]
    )
    mocker.patch.object(service_context.api, "list", return_value={"data": [mpt_item_data]})
    mocker.patch.object(
        service_context.api,
        "update",
        side_effect=MPTAPIError("API Error", "Error updating item"),
    )
    file_handler_mock = mocker.patch.object(service_context.file_manager, "write_error")

    result = ItemService(service_context).update()

    assert result.success is False
    assert any("Item" in item_error for item_error in result.errors)
    file_handler_mock.assert_called()


def test_update_item_not_found(mocker, service_context):
    mocker.patch.object(
        service_context.api, "list", side_effect=MPTAPIError("API Error", "Item not found")
    )
    file_handler_mock = mocker.patch.object(service_context.file_manager, "write_error")
    stats_spy = mocker.spy(service_context.stats, "add_error")
    service = ItemService(service_context)

    result = service.update()

    assert not result.success
    assert len(result.errors) > 0
    assert result.model is None
    file_handler_mock.assert_called()
    stats_spy.assert_called()


def test_update_item_skip(mocker, service_context, mpt_item_data, item_data_from_json):
    mocker.patch.object(
        service_context.file_manager, "read_data", return_value=[item_data_from_json]
    )
    mocker.patch.object(item_data_from_json, "to_update", return_value=False)
    write_ids_mock = mocker.spy(service_context.file_manager, "write_ids")
    api_update_spy = mocker.spy(service_context.api, "update")
    stats_spy = mocker.spy(service_context.stats, "add_skipped")
    service = ItemService(service_context)

    result = service.update()

    assert result.success is True
    write_ids_mock.assert_not_called()
    api_update_spy.assert_not_called()
    stats_spy.assert_called_once_with(TAB_PRICE_ITEMS)
