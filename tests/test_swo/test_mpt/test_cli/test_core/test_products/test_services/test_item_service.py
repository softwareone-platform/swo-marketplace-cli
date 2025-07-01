from unittest.mock import Mock

import pytest
from swo.mpt.cli.core.errors import MPTAPIError
from swo.mpt.cli.core.models import DataCollectionModel
from swo.mpt.cli.core.products.api import ItemAPIService
from swo.mpt.cli.core.products.constants import TAB_ITEMS
from swo.mpt.cli.core.products.handlers import ItemExcelFileManager
from swo.mpt.cli.core.products.models import ItemData
from swo.mpt.cli.core.products.models.items import ItemAction
from swo.mpt.cli.core.products.services import ItemService
from swo.mpt.cli.core.services.service_context import ServiceContext
from swo.mpt.cli.core.stats import ProductStatsCollector


@pytest.fixture
def service_context(mpt_client, product_file_path, active_vendor_account, item_data_from_dict):
    return ServiceContext(
        account=active_vendor_account,
        api=ItemAPIService(mpt_client, resource_id="test-product-id"),
        data_model=ItemData,
        file_manager=ItemExcelFileManager(product_file_path),
        stats=ProductStatsCollector(),
    )


def test_update_item_create(mocker, service_context, item_data_from_dict, mpt_item_data):
    item_data_from_dict.action = ItemAction.CREATE
    mocker.patch.object(
        service_context.file_manager, "read_data", return_value=[item_data_from_dict]
    )
    post_mock = mocker.patch.object(service_context.api, "post", return_value=mpt_item_data)
    search_uom_by_name_mock = mocker.patch(
        "swo.mpt.cli.core.products.services.item_service.search_uom_by_name",
        return_value=Mock(id="fake_unit_id"),
    )
    file_handler_write_mock = mocker.patch.object(service_context.file_manager, "write_id")
    update_spy = mocker.spy(service_context.api, "update")
    stats_spy = mocker.spy(service_context.stats, "add_synced")
    service = ItemService(service_context)

    result = service.update()

    assert result.success is True
    assert result.model is None
    assert service_context.stats.tabs["Items"]["synced"] == 1
    search_uom_by_name_mock.assert_called_once()
    post_mock.assert_called_once()
    file_handler_write_mock.assert_called_once_with(
        item_data_from_dict.coordinate, mpt_item_data["id"]
    )
    update_spy.assert_not_called()
    stats_spy.assert_called_once_with(TAB_ITEMS)


def test_update_item_create_error(mocker, service_context, item_data_from_dict):
    item_data_from_dict.action = ItemAction.CREATE
    mocker.patch.object(
        service_context.file_manager, "read_data", return_value=[item_data_from_dict]
    )
    post_mock = mocker.patch.object(
        service_context.api, "post", side_effect=MPTAPIError("API Error", "Error updating item")
    )
    search_uom_by_name_mock = mocker.patch(
        "swo.mpt.cli.core.products.services.item_service.search_uom_by_name",
        return_value=Mock(id="fake_unit_id"),
    )
    write_error_mock = mocker.patch.object(service_context.file_manager, "write_error")
    update_spy = mocker.spy(service_context.api, "update")
    add_error_spy = mocker.spy(service_context.stats, "add_error")
    service = ItemService(service_context)

    result = service.update()

    assert result.success is False
    assert service_context.stats.tabs["Items"]["error"] == 1
    search_uom_by_name_mock.assert_called_once()
    post_mock.assert_called_once()
    write_error_mock.assert_called_once()
    update_spy.assert_not_called()
    add_error_spy.assert_called_once_with(TAB_ITEMS)


def test_update_item_skip(mocker, service_context, item_data_from_dict, mpt_item_data):
    item_data_from_dict.action = ItemAction.SKIP
    mocker.patch.object(
        service_context.file_manager, "read_data", return_value=[item_data_from_dict]
    )
    stats_spy = mocker.spy(service_context.stats, "add_skipped")
    service = ItemService(service_context)

    result = service.update()

    assert result.success is True
    assert result.model is None
    assert service_context.stats.tabs["Items"]["skipped"] == 1
    stats_spy.assert_called_once_with(TAB_ITEMS)


def test_update_item_publish(mocker, service_context, item_data_from_dict, mpt_item_data):
    item_data_from_dict.action = ItemAction.PUBLISH
    mocker.patch.object(
        service_context.file_manager, "read_data", return_value=[item_data_from_dict]
    )
    post_action_mock = mocker.patch.object(service_context.api, "post_action")
    write_id_mock = mocker.patch.object(service_context.file_manager, "write_id")
    stats_spy = mocker.spy(service_context.stats, "add_synced")
    service = ItemService(service_context)

    result = service.update()

    assert result.success is True
    assert result.model is None
    assert service_context.stats.tabs["Items"]["synced"] == 1
    post_action_mock.assert_called_once_with(item_data_from_dict.id, ItemAction.PUBLISH)
    write_id_mock.assert_called_once_with(item_data_from_dict.coordinate, item_data_from_dict.id)
    stats_spy.assert_called_once_with(TAB_ITEMS)


def test_update_item_action_update(mocker, service_context, item_data_from_dict, mpt_item_data):
    item_data_from_dict.action = ItemAction.UPDATE
    mocker.patch.object(
        service_context.file_manager, "read_data", return_value=[item_data_from_dict]
    )
    mocker.patch.object(service_context.api, "list", return_value={"data": [mpt_item_data]})
    update_mock = mocker.patch.object(service_context.api, "update")
    file_handler_write_mock = mocker.patch.object(service_context.file_manager, "write_id")
    stats_spy = mocker.spy(service_context.stats, "add_synced")
    service = ItemService(service_context)

    result = service.update()

    assert result.success is True
    assert result.model is None
    assert service_context.stats.tabs["Items"]["synced"] == 1
    update_mock.assert_called_once()
    file_handler_write_mock.assert_called_once()
    stats_spy.assert_called_once_with(TAB_ITEMS)


def test_update_item_list_error(mocker, service_context, item_data_from_dict, mpt_item_data):
    item_data_from_dict.action = ItemAction.UPDATE
    read_data_mock = mocker.patch.object(
        service_context.file_manager, "read_data", return_value=[item_data_from_dict]
    )
    api_list_mock = mocker.patch.object(
        service_context.api, "list", side_effect=MPTAPIError("API Error", "Error getting items")
    )
    write_error_mock = mocker.patch.object(service_context.file_manager, "write_error")
    stats_add_error_spy = mocker.spy(service_context.stats, "add_error")
    service = ItemService(service_context)

    result = service.update()

    assert result.success is False
    assert result.errors == ["API Error with response body Error getting items"]
    assert result.model is None
    read_data_mock.assert_called_once()
    api_list_mock.assert_called_once_with(
        params={
            "externalIds.vendor": item_data_from_dict.vendor_id,
            "product.id": item_data_from_dict.product_id,
            "limit": 1,
        }
    )
    write_error_mock.assert_called()
    stats_add_error_spy.assert_called_once_with(TAB_ITEMS)


def test_update_item_update_error(mocker, service_context, item_data_from_dict, mpt_item_data):
    item_data_from_dict.action = ItemAction.UPDATE
    mocker.patch.object(service_context.api, "list", return_value={"data": [mpt_item_data]})
    read_data_mock = mocker.patch.object(
        service_context.file_manager, "read_data", return_value=[item_data_from_dict]
    )
    write_error_mock = mocker.patch.object(service_context.file_manager, "write_error")
    api_update_mock = mocker.patch.object(
        service_context.api, "update", side_effect=MPTAPIError("API Error", "Error updating item")
    )
    stats_add_error_spy = mocker.spy(service_context.stats, "add_error")
    stats_add_synced_spy = mocker.spy(service_context.stats, "add_synced")
    service = ItemService(service_context)

    result = service.update()

    assert result.success is False
    assert result.errors == ["API Error with response body Error updating item"]
    assert result.model is None
    read_data_mock.assert_called_once()
    api_update_mock.assert_called_once_with(item_data_from_dict.id, item_data_from_dict.to_json())
    write_error_mock.assert_called()
    stats_add_error_spy.assert_called_once_with(TAB_ITEMS)
    stats_add_synced_spy.assert_not_called()


def test_set_new_item_groups(
    mocker, service_context, item_data_from_dict, item_group_data_from_dict
):
    read_data_mock = mocker.patch.object(
        service_context.file_manager, "read_data", return_value=[item_data_from_dict]
    )
    param_group = DataCollectionModel(collection={"old_group_id": item_group_data_from_dict})
    item_data_from_dict.group_id = "old_group_id"
    write_id_mock = mocker.patch.object(service_context.file_manager, "write_id")
    service = ItemService(service_context)

    service.set_new_item_groups(param_group)

    read_data_mock.assert_called_once()
    write_id_mock.assert_called_once_with(
        item_data_from_dict.group_coordinate, item_group_data_from_dict.id
    )


def test_set_new_item_groups_error(
    mocker, service_context, item_data_from_dict, item_group_data_from_dict
):
    read_data_mock = mocker.patch.object(
        service_context.file_manager, "read_data", return_value=[item_data_from_dict]
    )
    param_group = DataCollectionModel(collection={"not_found_it": item_group_data_from_dict})
    write_id_mock = mocker.patch.object(service_context.file_manager, "write_id")
    service = ItemService(service_context)

    service.set_new_item_groups(param_group)

    read_data_mock.assert_called_once()
    write_id_mock.assert_not_called()


def test_set_export_params(service_context, item_data_from_dict):
    service = ItemService(service_context)

    params = service.set_export_params()

    assert params["product.id"] is not None


def test_prepare_data_model_to_create(mocker, service_context, item_data_from_dict):
    search_uom_by_name_mock = mocker.patch(
        "swo.mpt.cli.core.products.services.item_service.search_uom_by_name",
        return_value=Mock(id="fake_unit_id"),
    )
    write_id_mock = mocker.patch.object(service_context.file_manager, "write_id")
    service = ItemService(service_context)

    data_model = service.prepare_data_model_to_create(item_data_from_dict)

    assert data_model.unit_id == "fake_unit_id"
    assert data_model.item_type == "vendor"
    assert data_model.product_id == "test-product-id"
    search_uom_by_name_mock.assert_called_once()
    write_id_mock.assert_called_once_with(item_data_from_dict.unit_coordinate, "fake_unit_id")
