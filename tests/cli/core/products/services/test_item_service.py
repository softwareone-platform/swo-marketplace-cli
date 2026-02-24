from unittest.mock import Mock

import pytest
from cli.core.errors import MPTAPIError
from cli.core.models import DataCollectionModel
from cli.core.mpt.models import Uom
from cli.core.products.api import ItemAPIService
from cli.core.products.constants import TAB_ITEMS
from cli.core.products.handlers import ItemExcelFileManager
from cli.core.products.models import ItemActionEnum, ItemData
from cli.core.products.services import ItemService
from cli.core.services.service_context import ServiceContext
from cli.core.stats import ProductStatsCollector


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
    item_data_from_dict.action = ItemActionEnum.CREATE
    mocker.patch.object(
        service_context.file_manager, "read_data", return_value=[item_data_from_dict]
    )
    post_mock = mocker.patch.object(service_context.api, "post", return_value=mpt_item_data)
    search_uom_by_name_mock = mocker.patch(
        "cli.core.products.services.item_service.search_uom_by_name",
        return_value=Mock(id="fake_unit_id"),
    )
    write_ids_mock = mocker.patch.object(service_context.file_manager, "write_ids")
    update_spy = mocker.spy(service_context.api, "update")
    stats_spy = mocker.spy(service_context.stats, "add_synced")
    service = ItemService(service_context)

    result = service.update()

    assert result.success is True
    assert result.model is None
    assert service_context.stats.tabs["Items"]["synced"] == 1
    search_uom_by_name_mock.assert_called_once()
    post_mock.assert_called_once()
    write_ids_mock.assert_called_once_with({item_data_from_dict.coordinate: mpt_item_data["id"]})
    update_spy.assert_not_called()
    stats_spy.assert_called_once_with(TAB_ITEMS)


def test_update_item_create_error(mocker, service_context, item_data_from_dict):
    item_data_from_dict.action = ItemActionEnum.CREATE
    mocker.patch.object(
        service_context.file_manager, "read_data", return_value=[item_data_from_dict]
    )
    post_mock = mocker.patch.object(
        service_context.api, "post", side_effect=MPTAPIError("API Error", "Error updating item")
    )
    search_uom_by_name_mock = mocker.patch(
        "cli.core.products.services.item_service.search_uom_by_name",
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
    item_data_from_dict.action = ItemActionEnum.SKIP
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
    item_data_from_dict.action = ItemActionEnum.PUBLISH
    mocker.patch.object(
        service_context.file_manager, "read_data", return_value=[item_data_from_dict]
    )
    post_action_mock = mocker.patch.object(service_context.api, "post_action")
    write_ids_mock = mocker.patch.object(service_context.file_manager, "write_ids")
    stats_spy = mocker.spy(service_context.stats, "add_synced")
    service = ItemService(service_context)

    result = service.update()

    assert result.success is True
    assert result.model is None
    assert service_context.stats.tabs["Items"]["synced"] == 1
    post_action_mock.assert_called_once_with(item_data_from_dict.id, ItemActionEnum.PUBLISH)
    write_ids_mock.assert_called_once_with({item_data_from_dict.coordinate: item_data_from_dict.id})
    stats_spy.assert_called_once_with(TAB_ITEMS)


def test_set_new_item_groups(
    mocker, service_context, item_data_from_dict, item_group_data_from_dict
):
    read_data_mock = mocker.patch.object(
        service_context.file_manager, "read_data", return_value=[item_data_from_dict]
    )
    param_group = DataCollectionModel(collection={"old_group_id": item_group_data_from_dict})
    item_data_from_dict.group_id = "old_group_id"
    write_ids_mock = mocker.patch.object(service_context.file_manager, "write_ids")
    service = ItemService(service_context)

    service.set_new_item_groups(param_group)  # act

    read_data_mock.assert_called_once()
    write_ids_mock.assert_called_once_with({
        item_data_from_dict.group_coordinate: item_group_data_from_dict.id
    })


def test_set_new_item_groups_error(
    mocker, service_context, item_data_from_dict, item_group_data_from_dict
):
    read_data_mock = mocker.patch.object(
        service_context.file_manager, "read_data", return_value=[item_data_from_dict]
    )
    param_group = DataCollectionModel(collection={"not_found_it": item_group_data_from_dict})
    write_ids_spy = mocker.spy(service_context.file_manager, "write_ids")
    service = ItemService(service_context)

    service.set_new_item_groups(param_group)  # act

    read_data_mock.assert_called_once()
    write_ids_spy.assert_not_called()


def test_set_new_parameter_groups_empty(mocker, service_context):
    read_data_spy = mocker.spy(service_context.file_manager, "read_data")
    write_ids_spy = mocker.spy(service_context.file_manager, "write_ids")
    service = ItemService(service_context)

    service.set_new_item_groups(DataCollectionModel(collection={}))  # act

    read_data_spy.assert_not_called()
    write_ids_spy.assert_not_called()


def test_set_export_params(service_context, item_data_from_dict):
    service = ItemService(service_context)

    result = service.set_export_params()

    assert result["product.id"] is not None


def test_get_api_mpt_client_cached(mocker, service_context, item_data_from_dict):
    create_client_mock = mocker.patch(
        "cli.core.products.services.item_service.create_api_mpt_client_from_account"
    )
    mocker.patch(
        "cli.core.products.services.item_service.search_uom_by_name",
        return_value=Uom(id="fake_unit_id", name="fake_unit"),
    )
    mocker.patch.object(service_context.file_manager, "write_ids")
    service = ItemService(service_context)
    service.prepare_data_model_to_create(item_data_from_dict)

    service.prepare_data_model_to_create(item_data_from_dict)  # act

    create_client_mock.assert_called_once()


def test_prepare_data_model_to_create(mocker, service_context, item_data_from_dict):
    search_uom_by_name_mock = mocker.patch(
        "cli.core.products.services.item_service.search_uom_by_name",
        return_value=Mock(id="fake_unit_id"),
    )
    write_ids_mock = mocker.patch.object(service_context.file_manager, "write_ids")
    service = ItemService(service_context)

    result = service.prepare_data_model_to_create(item_data_from_dict)

    assert result.unit_id == "fake_unit_id"
    assert result.item_type == "vendor"
    assert result.product_id == "test-product-id"
    search_uom_by_name_mock.assert_called_once()
    write_ids_mock.assert_called_once_with({item_data_from_dict.unit_coordinate: "fake_unit_id"})
