from unittest.mock import Mock, call

import pytest
from cli.core.errors import MPTAPIError
from cli.core.handlers.errors import RequiredFieldsError, RequiredSheetsError
from cli.core.products.api import ProductAPIService
from cli.core.products.constants import TAB_GENERAL
from cli.core.products.handlers import ProductExcelFileManager, SettingsExcelFileManager
from cli.core.products.models import ProductData
from cli.core.products.services import ProductService
from cli.core.services.service_context import ServiceContext
from cli.core.stats import ProductStatsCollector
from freezegun import freeze_time


@pytest.fixture
def service_context(mock_mpt_api_client, product_new_file, active_vendor_account):
    stats = ProductStatsCollector()
    return ServiceContext(
        account=active_vendor_account,
        api=ProductAPIService(mock_mpt_api_client),
        data_model=ProductData,
        file_manager=ProductExcelFileManager(product_new_file),
        stats=stats,
    )


@pytest.fixture
def product_service(service_context):
    return ProductService(service_context)


def test_create(mocker, service_context, product_service, mpt_product_data, product_data_from_dict):
    mocker.patch.object(
        service_context.file_manager, "read_data", return_value=product_data_from_dict
    )
    mocker.patch.object(service_context.api, "post", return_value=mpt_product_data)
    mocker.patch.object(service_context.api, "update")
    mocker.patch.object(service_context.file_manager, "write_ids")
    mocker.spy(service_context.stats, "add_synced")

    result = product_service.create()

    assert result.success is True
    service_context.file_manager.read_data.assert_called_once()
    service_context.stats.add_synced.assert_called_once_with(TAB_GENERAL)
    service_context.file_manager.write_ids.assert_called_once_with({
        "B3": product_data_from_dict.id
    })
    service_context.api.post.assert_called_once()
    service_context.api.update.assert_called_once()


def test_create_post_error(mocker, service_context, product_service, product_data_from_dict):
    read_data_mock = mocker.patch.object(
        service_context.file_manager, "read_data", return_value=product_data_from_dict
    )
    api_post_mock = mocker.patch.object(
        service_context.api,
        "post",
        side_effect=MPTAPIError("API Error", "Error creating product"),
    )
    file_handler_write_mock = mocker.patch.object(service_context.file_manager, "write_error")
    stats_spy = mocker.spy(service_context.stats, "add_error")

    result = product_service.create()

    assert not result.success
    assert result.errors == ["API Error with response body Error creating product"]
    assert result.model is None
    stats_spy.assert_called_once_with(TAB_GENERAL)
    read_data_mock.assert_called_once()
    api_post_mock.assert_called_once()
    file_handler_write_mock.assert_called_once()


def test_create_update_error(
    mocker, service_context, product_service, mpt_product_data, product_data_from_dict
):
    mocker.patch.object(
        service_context.file_manager, "read_data", return_value=product_data_from_dict
    )
    mocker.patch.object(service_context.api, "post", return_value=mpt_product_data)
    mocker.patch.object(
        service_context.api,
        "update",
        side_effect=MPTAPIError("API Error", "Error creating product"),
    )
    mocker.patch.object(service_context.file_manager, "write_error")
    mocker.spy(service_context.stats, "add_error")

    result = product_service.create()

    assert result.success is False
    assert result.errors == ["API Error with response body Error creating product"]
    assert result.model is None
    service_context.stats.add_error.assert_called_once_with(TAB_GENERAL)
    service_context.file_manager.read_data.assert_called_once()
    service_context.api.post.assert_called_once()
    service_context.api.update.assert_called_once()
    service_context.file_manager.write_error.assert_called_once()


def test_export(mocker, service_context, product_service, mpt_product_data):
    mocker.patch.object(service_context.api, "get", return_value=mpt_product_data)
    mocker.patch.object(service_context.file_manager, "create_tab")
    mocker.patch.object(service_context.file_manager, "add")
    mocker.patch.object(SettingsExcelFileManager, "create_tab")
    mocker.patch.object(SettingsExcelFileManager, "add")

    result = product_service.export({"product_id": "fake_id"})

    assert result.success is True
    service_context.api.get.assert_called()
    service_context.file_manager.create_tab.assert_called_once()
    service_context.file_manager.add.assert_called_once()
    SettingsExcelFileManager.create_tab.assert_called_once()
    SettingsExcelFileManager.add.assert_called_once()


def test_export_mpt_error(mocker, service_context, product_service):
    get_mock = mocker.patch.object(
        service_context.api, "get", side_effect=MPTAPIError("API Error", "Error retrieving item")
    )
    create_tab_spy = mocker.spy(service_context.file_manager, "create_tab")
    add_spy = mocker.spy(service_context.file_manager, "add")

    result = product_service.export({"product_id": "fake_id"})

    assert result.success is False
    get_mock.assert_called_once()
    create_tab_spy.assert_not_called()
    add_spy.assert_not_called()


def test_validate_definition(mocker, service_context, product_service):
    mocker.patch.object(service_context.file_manager, "check_required_tabs")
    mocker.patch.object(service_context.file_manager, "check_required_fields_by_section")

    result = product_service.validate_definition()

    assert result.success is True
    assert result.errors == []
    assert result.model is None


def test_validate_definition_file_doesnt_exist(mocker, service_context, product_service):
    mocker.patch.object(service_context.file_manager.file_handler, "exists", return_value=False)

    result = product_service.validate_definition()

    assert result.success is False
    assert result.errors == ["Provided file path doesn't exist"]


def test_validate_definition_missing_tabs(mocker, service_context, product_service):
    mocker.patch.object(
        service_context.file_manager,
        "check_required_tabs",
        side_effect=RequiredSheetsError("Required tabs missing", ["Tab1", "Tab2"]),
    )
    check_required_fields_by_section_spy = mocker.spy(
        service_context.file_manager, "check_required_fields_by_section"
    )
    stats_spy = mocker.spy(service_context.stats.errors, "add_msg")

    result = product_service.validate_definition()

    assert result.success is False
    assert result.errors == ["('Required tabs missing', ['Tab1', 'Tab2'])"]
    stats_spy.assert_has_calls([
        call("Tab1", "", "Required tab doesn't exist"),
        call("Tab2", "", "Required tab doesn't exist"),
    ])
    check_required_fields_by_section_spy.assert_not_called()


def test_validate_definition_missing_fields(mocker, service_context, product_service):
    check_required_tabs_mock = mocker.patch.object(
        service_context.file_manager, "check_required_tabs"
    )
    mocker.patch.object(
        service_context.file_manager,
        "check_required_fields_by_section",
        side_effect=RequiredFieldsError("Required fields missing", ["Field1", "Field2"]),
    )
    stats_spy = mocker.spy(service_context.stats.errors, "add_msg")

    result = product_service.validate_definition()

    assert result.success is False
    assert result.errors == ["('Required fields missing', ['Field1', 'Field2'])"]
    stats_spy.assert_has_calls([
        call("Field1", "", "Required field doesn't exist"),
        call("Field2", "", "Required field doesn't exist"),
    ])
    check_required_tabs_mock.assert_called_once()


def test_retrieve(mocker, service_context, product_service, product_data_from_dict):
    read_data_mock = mocker.patch.object(
        service_context.file_manager, "read_data", return_value=product_data_from_dict
    )
    api_exists_mock = mocker.patch.object(
        service_context.api,
        "exists",
        return_value=True,
    )

    result = product_service.retrieve()

    assert result.success is True
    assert result.model == product_data_from_dict
    read_data_mock.assert_called_once()
    api_exists_mock.assert_called_once()


def test_retrieve_empty(mocker, service_context, product_service):
    read_data_mock = mocker.patch.object(
        service_context.file_manager, "read_data", return_value=Mock(ProductData, id=None)
    )
    api_exists_mock = mocker.spy(service_context.api, "exists")

    result = product_service.retrieve()

    assert result.success is True
    assert result.model is None
    read_data_mock.assert_called_once()
    api_exists_mock.assert_not_called()


def test_retrieve_not_found(mocker, service_context, product_service):
    mocker.patch.object(
        service_context.api, "exists", side_effect=MPTAPIError("Not Found", "Product not found")
    )
    file_handler_write_mock = mocker.patch.object(service_context.file_manager, "write_error")

    result = product_service.retrieve()

    assert not result.success
    assert len(result.errors) > 0
    file_handler_write_mock.assert_called_once()


@freeze_time("2025-05-30")
def test_retrieve_from_mpt(
    mocker, service_context, product_service, mpt_product_data, product_data_from_json
):
    api_get_mock = mocker.patch.object(
        service_context.api,
        "get",
        return_value=mpt_product_data,
    )

    result = product_service.retrieve_from_mpt(product_data_from_json.id)

    assert result.success is True
    assert result.model == product_data_from_json
    api_get_mock.assert_called_once_with(product_data_from_json.id)


def test_retrieve_from_mpt_error(mocker, service_context, product_service):
    api_get_mock = mocker.patch.object(
        service_context.api,
        "get",
        side_effect=MPTAPIError("API Error", "Error retrieving item"),
    )

    result = product_service.retrieve_from_mpt("fake_id")

    assert result.success is False
    assert len(result.errors) > 0
    assert result.model is None
    api_get_mock.assert_called_once_with("fake_id")


def test_update(mocker, service_context, product_service, product_data_from_dict):
    read_data_mock = mocker.patch.object(
        service_context.file_manager, "read_data", return_value=product_data_from_dict
    )
    read_settings_data_mock = mocker.patch.object(
        SettingsExcelFileManager, "read_data", return_value=iter([product_data_from_dict.settings])
    )
    api_update_mock = mocker.patch.object(service_context.api, "update")

    result = product_service.update()

    assert result.success is True
    assert result.model is not None
    read_data_mock.assert_called_once()
    read_settings_data_mock.assert_called_once()
    expected_data = {
        "settings": {
            "preValidation": {"changeOrderDraft": True},
        }
    }
    api_update_mock.assert_called_once_with(product_data_from_dict.id, expected_data)


def test_update_error(mocker, service_context, product_service, product_data_from_dict):
    mocker.patch.object(service_context.file_manager, "read_data", return_value=Mock(id=None))
    mocker.patch.object(
        SettingsExcelFileManager, "read_data", return_value=iter([product_data_from_dict.settings])
    )
    mocker.patch.object(
        service_context.api,
        "update",
        side_effect=MPTAPIError("API Error", "Error updating product"),
    )
    mocker.spy(service_context.stats, "add_error")
    mocker.patch.object(service_context.file_manager, "write_error")

    result = product_service.update()

    assert result.success is False
    assert result.errors == ["API Error with response body Error updating product"]
    assert result.model is None
    service_context.file_manager.read_data.assert_called_once()
    SettingsExcelFileManager.read_data.assert_called_once()
    service_context.stats.add_error.assert_called_once_with(TAB_GENERAL)
    service_context.file_manager.write_error.assert_called_once()
    service_context.api.update.assert_called_once()
