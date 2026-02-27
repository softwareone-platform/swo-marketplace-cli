from unittest.mock import Mock, call

import pytest
from cli.core.handlers.errors import RequiredFieldsError, RequiredSheetsError
from cli.core.products.api import ProductAPIService
from cli.core.products.constants import TAB_GENERAL
from cli.core.products.handlers import ProductExcelFileManager, SettingsExcelFileManager
from cli.core.products.models import ProductData
from cli.core.products.services import ProductService
from cli.core.services.service_context import ServiceContext
from cli.core.stats import ProductStatsCollector
from freezegun import freeze_time
from mpt_api_client.exceptions import MPTAPIError
from mpt_api_client.resources.catalog.products import Product


@pytest.fixture
def service_context(mpt_client, product_new_file, active_vendor_account):
    stats = ProductStatsCollector()
    return ServiceContext(
        account=active_vendor_account,
        api=ProductAPIService(mpt_client),
        data_model=ProductData,
        file_manager=ProductExcelFileManager(product_new_file),
        stats=stats,
    )


def test_create(mocker, service_context, mpt_product_data, product_data_from_dict, api_mpt_client):
    read_data_mock = mocker.patch.object(
        service_context.file_manager, "read_data", return_value=product_data_from_dict
    )
    product_obj = mocker.Mock(spec=Product)
    product_obj.id = mpt_product_data["id"]
    api_mpt_client.catalog.products.create.return_value = product_obj
    mocker.patch(
        "cli.core.products.services.product_service.create_api_mpt_client_from_account",
        return_value=api_mpt_client,
    )
    write_id_mock = mocker.patch.object(service_context.file_manager, "write_ids")
    stats_spy = mocker.spy(service_context.stats, "add_synced")
    service = ProductService(service_context)

    result = service.create()

    assert result.success is True
    read_data_mock.assert_called_once()
    stats_spy.assert_called_once_with(TAB_GENERAL)
    write_id_mock.assert_called_once_with({"B3": product_data_from_dict.id})
    api_mpt_client.catalog.products.create.assert_called_once()
    api_mpt_client.catalog.products.update_settings.assert_called_once()


def test_create_post_error(
    mocker,
    service_context,
    product_data_from_dict,
    api_mpt_client,
    mock_mpt_client_error_payload,
):
    read_data_mock = mocker.patch.object(
        service_context.file_manager, "read_data", return_value=product_data_from_dict
    )
    err_status = mock_mpt_client_error_payload["status"]
    err_message = mock_mpt_client_error_payload["message"]
    api_mpt_client.catalog.products.create.side_effect = MPTAPIError(
        err_status, err_message, mock_mpt_client_error_payload
    )
    mocker.patch(
        "cli.core.products.services.product_service.create_api_mpt_client_from_account",
        return_value=api_mpt_client,
    )
    file_handler_write_mock = mocker.patch.object(service_context.file_manager, "write_error")
    stats_spy = mocker.spy(service_context.stats, "add_error")
    service = ProductService(service_context)

    result = service.create()

    assert result.success is False
    assert len(result.errors) > 0
    assert result.model is product_data_from_dict
    stats_spy.assert_called_once_with(TAB_GENERAL)
    read_data_mock.assert_called_once()
    api_mpt_client.catalog.products.create.assert_called_once()
    file_handler_write_mock.assert_called_once()


def test_create_update_error(
    mocker,
    service_context,
    mpt_product_data,
    product_data_from_dict,
    api_mpt_client,
    mock_mpt_client_error_payload,
):
    read_data_mock = mocker.patch.object(
        service_context.file_manager, "read_data", return_value=product_data_from_dict
    )
    err_status = mock_mpt_client_error_payload["status"]
    err_message = mock_mpt_client_error_payload["message"]
    product_obj = mocker.Mock(spec=Product)
    product_obj.id = mpt_product_data["id"]
    api_mpt_client.catalog.products.create.return_value = product_obj
    api_mpt_client.catalog.products.update_settings.side_effect = MPTAPIError(
        err_status, err_message, mock_mpt_client_error_payload
    )
    mocker.patch(
        "cli.core.products.services.product_service.create_api_mpt_client_from_account",
        return_value=api_mpt_client,
    )
    file_handler_write_mock = mocker.patch.object(service_context.file_manager, "write_error")
    stats_spy = mocker.spy(service_context.stats, "add_error")
    service = ProductService(service_context)

    result = service.create()

    assert result.success is False
    assert len(result.errors) > 0
    assert result.model is None
    stats_spy.assert_called_once_with(TAB_GENERAL)
    read_data_mock.assert_called_once()
    api_mpt_client.catalog.products.create.assert_called_once()
    api_mpt_client.catalog.products.update_settings.assert_called_once()
    file_handler_write_mock.assert_called_once()


def test_export(mocker, service_context, mpt_product_data, api_mpt_client):
    api_mpt_client.catalog.products.get.return_value = Product(mpt_product_data)
    mocker.patch(
        "cli.core.products.services.product_service.create_api_mpt_client_from_account",
        return_value=api_mpt_client,
    )
    create_tab_mock = mocker.patch.object(service_context.file_manager, "create_tab")
    add_mock = mocker.patch.object(service_context.file_manager, "add")
    settings_create_tab_mock = mocker.patch.object(SettingsExcelFileManager, "create_tab")
    settings_file_manager_add_mock = mocker.patch.object(SettingsExcelFileManager, "add")
    service = ProductService(service_context)

    result = service.export("fake_id")

    assert result.success is True
    api_mpt_client.catalog.products.get.assert_called_once_with("fake_id")
    create_tab_mock.assert_called_once()
    add_mock.assert_called_once()
    settings_create_tab_mock.assert_called_once()
    settings_file_manager_add_mock.assert_called_once()


def test_export_mpt_error(mocker, service_context, mock_mpt_client_error_payload, api_mpt_client):
    err_message = mock_mpt_client_error_payload["message"]
    err_status = mock_mpt_client_error_payload["status"]
    api_mpt_client.catalog.products.get.side_effect = MPTAPIError(
        err_status, err_message, mock_mpt_client_error_payload
    )
    mocker.patch(
        "cli.core.products.services.product_service.create_api_mpt_client_from_account",
        return_value=api_mpt_client,
    )
    create_tab_spy = mocker.spy(service_context.file_manager, "create_tab")
    add_spy = mocker.spy(service_context.file_manager, "add")
    service = ProductService(service_context)

    result = service.export("fake_id")

    assert result.success is False
    api_mpt_client.catalog.products.get.assert_called_once_with("fake_id")
    create_tab_spy.assert_not_called()
    add_spy.assert_not_called()


def test_validate_definition(mocker, service_context):
    mocker.patch.object(service_context.file_manager, "check_required_tabs")
    mocker.patch.object(service_context.file_manager, "check_required_fields_by_section")
    service = ProductService(service_context)

    result = service.validate_definition()

    assert result.success is True
    assert result.errors == []
    assert result.model is None


def test_validate_definition_file_doesnt_exist(mocker, service_context):
    mocker.patch.object(service_context.file_manager.file_handler, "exists", return_value=False)
    service = ProductService(service_context)

    result = service.validate_definition()

    assert result.success is False
    assert result.errors == ["Provided file path doesn't exist"]


def test_validate_definition_missing_tabs(mocker, service_context):
    mocker.patch.object(
        service_context.file_manager,
        "check_required_tabs",
        side_effect=RequiredSheetsError("Required tabs missing", ["Tab1", "Tab2"]),
    )
    check_required_fields_by_section_spy = mocker.spy(
        service_context.file_manager, "check_required_fields_by_section"
    )
    stats_spy = mocker.spy(service_context.stats.errors, "add_msg")
    service = ProductService(service_context)

    result = service.validate_definition()

    assert result.success is False
    assert result.errors == ["('Required tabs missing', ['Tab1', 'Tab2'])"]
    stats_spy.assert_has_calls([
        call("Tab1", "", "Required tab doesn't exist"),
        call("Tab2", "", "Required tab doesn't exist"),
    ])
    check_required_fields_by_section_spy.assert_not_called()


def test_validate_definition_missing_fields(mocker, service_context):
    check_required_tabs_mock = mocker.patch.object(
        service_context.file_manager, "check_required_tabs"
    )
    mocker.patch.object(
        service_context.file_manager,
        "check_required_fields_by_section",
        side_effect=RequiredFieldsError("Required fields missing", ["Field1", "Field2"]),
    )
    stats_spy = mocker.spy(service_context.stats.errors, "add_msg")
    service = ProductService(service_context)

    result = service.validate_definition()

    assert result.success is False
    assert result.errors == ["('Required fields missing', ['Field1', 'Field2'])"]
    stats_spy.assert_has_calls([
        call("Field1", "", "Required field doesn't exist"),
        call("Field2", "", "Required field doesn't exist"),
    ])
    check_required_tabs_mock.assert_called_once()


def test_retrieve(mocker, service_context, product_data_from_dict, api_mpt_client):
    read_data_mock = mocker.patch.object(
        service_context.file_manager, "read_data", return_value=product_data_from_dict
    )
    filter_result = api_mpt_client.catalog.products.filter.return_value
    fetch_page_mock = filter_result.fetch_page
    fetch_page_mock.return_value.meta.pagination.total = 1
    mocker.patch(
        "cli.core.products.services.product_service.create_api_mpt_client_from_account",
        return_value=api_mpt_client,
    )
    service = ProductService(service_context)

    result = service.retrieve()

    assert result.success is True
    assert result.model == product_data_from_dict
    read_data_mock.assert_called_once()
    fetch_page_mock.assert_called_once_with(limit=0)


def test_retrieve_empty(mocker, service_context, api_mpt_client):
    read_data_mock = mocker.patch.object(
        service_context.file_manager,
        "read_data",
        return_value=mocker.Mock(spec=ProductData, id=None),
    )
    mocker.patch(
        "cli.core.products.services.product_service.create_api_mpt_client_from_account",
        return_value=api_mpt_client,
    )
    service = ProductService(service_context)

    result = service.retrieve()

    assert result.success is True
    assert result.model is None
    read_data_mock.assert_called_once()
    api_mpt_client.catalog.products.filter.assert_not_called()


def test_retrieve_not_found(
    mocker,
    service_context,
    product_data_from_dict,
    api_mpt_client,
    mock_mpt_client_error_payload,
):
    mocker.patch.object(
        service_context.file_manager, "read_data", return_value=product_data_from_dict
    )
    err_status = mock_mpt_client_error_payload["status"]
    err_message = mock_mpt_client_error_payload["message"]
    filter_result = api_mpt_client.catalog.products.filter.return_value
    fetch_page_mock = filter_result.fetch_page
    fetch_page_mock.side_effect = MPTAPIError(
        err_status, err_message, mock_mpt_client_error_payload
    )
    mocker.patch(
        "cli.core.products.services.product_service.create_api_mpt_client_from_account",
        return_value=api_mpt_client,
    )
    file_handler_write_mock = mocker.patch.object(service_context.file_manager, "write_error")
    service = ProductService(service_context)

    result = service.retrieve()

    assert not result.success
    assert len(result.errors) > 0
    file_handler_write_mock.assert_called_once()


@freeze_time("2025-05-30")
def test_retrieve_from_mpt(
    mocker, service_context, mpt_product_data, product_data_from_json, api_mpt_client
):
    expected_product = Product(mpt_product_data)
    api_mpt_client.catalog.products.get.return_value = expected_product
    mocker.patch(
        "cli.core.products.services.product_service.create_api_mpt_client_from_account",
        return_value=api_mpt_client,
    )
    service = ProductService(service_context)

    result = service.retrieve_from_mpt(product_data_from_json.id)

    assert result.success is True
    assert result.model is expected_product
    api_mpt_client.catalog.products.get.assert_called_once_with(product_data_from_json.id)


def test_retrieve_from_mpt_error(
    mocker, service_context, api_mpt_client, mock_mpt_client_error_payload
):
    err_status = mock_mpt_client_error_payload["status"]
    err_message = mock_mpt_client_error_payload["message"]
    api_mpt_client.catalog.products.get.side_effect = MPTAPIError(
        err_status, err_message, mock_mpt_client_error_payload
    )
    mocker.patch(
        "cli.core.products.services.product_service.create_api_mpt_client_from_account",
        return_value=api_mpt_client,
    )
    service = ProductService(service_context)

    result = service.retrieve_from_mpt("fake_id")

    assert result.success is False
    assert len(result.errors) > 0
    assert result.model is None
    api_mpt_client.catalog.products.get.assert_called_once_with("fake_id")


def test_update(mocker, service_context, product_data_from_dict, api_mpt_client):
    read_data_mock = mocker.patch.object(
        service_context.file_manager, "read_data", return_value=product_data_from_dict
    )
    read_settings_data_mock = mocker.patch.object(
        SettingsExcelFileManager, "read_data", return_value=iter([product_data_from_dict.settings])
    )
    mocker.patch(
        "cli.core.products.services.product_service.create_api_mpt_client_from_account",
        return_value=api_mpt_client,
    )
    service = ProductService(service_context)

    result = service.update()

    assert result.success is True
    assert result.model is not None
    read_data_mock.assert_called_once()
    read_settings_data_mock.assert_called_once()
    expected_data = {
        "settings": {
            "preValidation": {"changeOrderDraft": True},
        }
    }
    api_mpt_client.catalog.products.update_settings.assert_called_once_with(
        product_data_from_dict.id, expected_data
    )


def test_update_error(
    mocker,
    service_context,
    product_data_from_dict,
    api_mpt_client,
    mock_mpt_client_error_payload,
):
    read_data_mock = mocker.patch.object(
        service_context.file_manager, "read_data", autospec=True, return_value=Mock(id=None)
    )
    read_settings_data_mock = mocker.patch.object(
        SettingsExcelFileManager, "read_data", return_value=iter([product_data_from_dict.settings])
    )
    err_status = mock_mpt_client_error_payload["status"]
    err_message = mock_mpt_client_error_payload["message"]
    api_mpt_client.catalog.products.update_settings.side_effect = MPTAPIError(
        err_status, err_message, mock_mpt_client_error_payload
    )
    mocker.patch(
        "cli.core.products.services.product_service.create_api_mpt_client_from_account",
        return_value=api_mpt_client,
    )
    stats_spy = mocker.spy(service_context.stats, "add_error")
    file_handler_write_mock = mocker.patch.object(service_context.file_manager, "write_error")
    service = ProductService(service_context)

    result = service.update()

    assert result.success is False
    assert len(result.errors) > 0
    assert result.model is None
    read_data_mock.assert_called_once()
    read_settings_data_mock.assert_called_once()
    stats_spy.assert_called_once_with(TAB_GENERAL)
    file_handler_write_mock.assert_called_once()
    api_mpt_client.catalog.products.update_settings.assert_called_once()
