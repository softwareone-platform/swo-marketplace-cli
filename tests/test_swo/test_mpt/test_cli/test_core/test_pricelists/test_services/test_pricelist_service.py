import pytest
from swo.mpt.cli.core.errors import MPTAPIError
from swo.mpt.cli.core.price_lists.api import PriceListAPIService
from swo.mpt.cli.core.price_lists.constants import TAB_GENERAL
from swo.mpt.cli.core.price_lists.handlers import PriceListExcelFileManager
from swo.mpt.cli.core.price_lists.models import PriceListData
from swo.mpt.cli.core.price_lists.services import PriceListService
from swo.mpt.cli.core.services.service_context import ServiceContext
from swo.mpt.cli.core.stats import PriceListStatsCollector


@pytest.fixture
def service_context(mpt_client, price_list_new_file, active_vendor_account):
    stats = PriceListStatsCollector()
    return ServiceContext(
        account=active_vendor_account,
        api=PriceListAPIService(mpt_client),
        data_model=PriceListData,
        file_manager=PriceListExcelFileManager(price_list_new_file),
        stats=stats,
    )


def test_create_price_list(mocker, service_context, mpt_price_list_data, price_list_data_from_dict):
    read_general_data_mock = mocker.patch.object(
        service_context.file_manager, "read_general_data", return_value=price_list_data_from_dict
    )
    api_post_mock = mocker.patch.object(
        service_context.api,
        "post",
        return_value=mpt_price_list_data,
    )
    file_handler_write_mock = mocker.patch.object(service_context.file_manager, "write_id")
    stats_spy = mocker.spy(service_context.stats, "add_synced")
    service = PriceListService(service_context)

    result = service.create()

    assert result.success is True
    read_general_data_mock.assert_called_once()
    stats_spy.assert_called_once_with(TAB_GENERAL)
    file_handler_write_mock.assert_called_once_with("B3", price_list_data_from_dict.id)
    api_post_mock.assert_called_once()


def test_create_price_list_error(mocker, service_context, price_list_data_from_dict):
    read_general_data_mock = mocker.patch.object(
        service_context.file_manager, "read_general_data", return_value=price_list_data_from_dict
    )
    api_post_mock = mocker.patch.object(
        service_context.api,
        "post",
        side_effect=MPTAPIError("API Error", "Error creating price list"),
    )
    file_handler_write_mock = mocker.patch.object(service_context.file_manager, "write_error")
    stats_spy = mocker.spy(service_context.stats, "add_error")
    service = PriceListService(service_context)

    result = service.create()

    assert result.success is False
    assert result.errors == ["API Error with response body Error creating price list"]
    assert result.model is None
    stats_spy.assert_called_once_with(TAB_GENERAL)
    read_general_data_mock.assert_called_once()
    api_post_mock.assert_called_once()
    file_handler_write_mock.assert_called_once()


def test_export(mocker, service_context, mpt_price_list_data):
    get_mock = mocker.patch.object(service_context.api, "get", return_value=mpt_price_list_data)
    create_tab_mock = mocker.patch.object(service_context.file_manager, "create_tab")
    add_mock = mocker.patch.object(service_context.file_manager, "add")
    service = PriceListService(service_context)

    result = service.export({"price_list_id": "fake_id"})

    assert result.success is True
    get_mock.assert_called()
    create_tab_mock.assert_called_once()
    add_mock.assert_called_once()


def test_export_mpt_error(mocker, service_context):
    get_mock = mocker.patch.object(
        service_context.api, "get", side_effect=MPTAPIError("API Error", "Error retrieving item")
    )
    create_tab_spy = mocker.spy(service_context.file_manager, "create_tab")
    add_spy = mocker.spy(service_context.file_manager, "add")
    service = PriceListService(service_context)

    result = service.export({"price_list_id": "fake_id"})

    assert result.success is False
    get_mock.assert_called_once()
    create_tab_spy.assert_not_called()
    add_spy.assert_not_called()


def test_retrieve_price_list(mocker, service_context, price_list_data_from_dict):
    read_general_data_mock = mocker.patch.object(
        service_context.file_manager, "read_general_data", return_value=price_list_data_from_dict
    )
    api_exists_mock = mocker.patch.object(
        service_context.api,
        "exists",
        return_value=True,
    )

    service = PriceListService(service_context)

    result = service.retrieve()

    assert result.success is True
    assert result.model == price_list_data_from_dict
    read_general_data_mock.assert_called_once()
    api_exists_mock.assert_called_once()


def test_retrieve_price_list_not_found(mocker, service_context):
    mocker.patch.object(
        service_context.api, "exists", side_effect=MPTAPIError("Not Found", "Pricelist not found")
    )
    file_handler_write_mock = mocker.patch.object(service_context.file_manager, "write_error")
    service = PriceListService(service_context)

    result = service.retrieve()

    assert not result.success
    assert len(result.errors) > 0
    file_handler_write_mock.assert_called_once()


def test_retrieve_from_mpt(mocker, service_context, mpt_price_list_data, price_list_data_from_json):
    api_get_mock = mocker.patch.object(
        service_context.api,
        "get",
        return_value=mpt_price_list_data,
    )
    service = PriceListService(service_context)

    result = service.retrieve_from_mpt(price_list_data_from_json.id)

    assert result.success is True
    assert result.model == price_list_data_from_json
    api_get_mock.assert_called_once_with(price_list_data_from_json.id)


def test_retrieve_from_mpt_error(mocker, service_context):
    api_get_mock = mocker.patch.object(
        service_context.api,
        "get",
        side_effect=MPTAPIError("API Error", "Error retrieving item"),
    )
    service = PriceListService(service_context)

    result = service.retrieve_from_mpt("fake_id")

    assert result.success is False
    assert len(result.errors) > 0
    assert result.model is None
    api_get_mock.assert_called_once_with("fake_id")


def test_update_price_list(mocker, service_context, price_list_data_from_dict):
    read_general_data_mock = mocker.patch.object(
        service_context.file_manager, "read_general_data", return_value=price_list_data_from_dict
    )
    api_update_mock = mocker.patch.object(service_context.api, "update")
    service = PriceListService(service_context)

    result = service.update(price_list_data_from_dict.id)

    assert result.success is True
    assert result.model is not None
    read_general_data_mock.assert_called_once()
    api_update_mock.assert_called_once()


def test_update_price_list_error(mocker, service_context, price_list_data_from_dict):
    read_general_data_mock = mocker.patch.object(
        service_context.file_manager, "read_general_data", return_value=price_list_data_from_dict
    )
    api_update_mock = mocker.patch.object(
        service_context.api,
        "update",
        side_effect=MPTAPIError("API Error", "Error updating price list"),
    )
    stats_spy = mocker.spy(service_context.stats, "add_error")
    file_handler_write_mock = mocker.patch.object(service_context.file_manager, "write_error")
    service = PriceListService(service_context)

    result = service.update(price_list_data_from_dict.id)

    assert result.success is False
    assert result.errors == ["API Error with response body Error updating price list"]
    assert result.model is None
    read_general_data_mock.assert_called_once()
    stats_spy.assert_called_once_with(TAB_GENERAL)
    file_handler_write_mock.assert_called_once()
    api_update_mock.assert_called_once()
