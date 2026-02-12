import pytest
from cli.core.models import DataCollectionModel
from cli.core.products.api import ParametersAPIService
from cli.core.products.handlers import AgreementParametersExcelFileManager
from cli.core.products.models import AgreementParametersData
from cli.core.products.services import ParametersService
from cli.core.services.service_context import ServiceContext
from cli.core.stats import ProductStatsCollector


@pytest.fixture
def service_context(mpt_client, product_file_path, active_vendor_account):
    return ServiceContext(
        account=active_vendor_account,
        api=ParametersAPIService(mpt_client, resource_id="test-product-id"),
        data_model=AgreementParametersData,
        file_manager=AgreementParametersExcelFileManager(product_file_path),
        stats=ProductStatsCollector(),
    )


def test_set_new_parameter_groups(
    mocker, service_context, parameters_data_from_dict, parameter_group_data_from_dict
):
    read_data_mock = mocker.patch.object(
        service_context.file_manager, "read_data", return_value=[parameters_data_from_dict]
    )
    param_group = DataCollectionModel(collection={"old_group_id": parameter_group_data_from_dict})
    parameters_data_from_dict.group_id = "old_group_id"
    write_ids_mock = mocker.patch.object(service_context.file_manager, "write_ids")
    service = ParametersService(service_context)

    service.set_new_parameter_group(param_group)  # act

    read_data_mock.assert_called_once()
    write_ids_mock.assert_called_once_with({
        parameters_data_from_dict.group_id_coordinate: parameter_group_data_from_dict.id
    })


def test_set_new_parameter_groups_error(
    mocker, service_context, parameters_data_from_dict, parameter_group_data_from_dict
):
    read_data_mock = mocker.patch.object(
        service_context.file_manager, "read_data", return_value=[parameters_data_from_dict]
    )
    param_group = DataCollectionModel(collection={"not_found_key": parameter_group_data_from_dict})
    write_ids_spy = mocker.spy(service_context.file_manager, "write_ids")
    service = ParametersService(service_context)

    service.set_new_parameter_group(param_group)  # act

    read_data_mock.assert_called_once()
    write_ids_spy.assert_not_called()


def test_set_new_parameter_groups_empty(mocker, service_context):
    read_data_spy = mocker.spy(service_context.file_manager, "read_data")
    write_ids_spy = mocker.spy(service_context.file_manager, "write_ids")
    service = ParametersService(service_context)

    service.set_new_parameter_group(DataCollectionModel(collection={}))  # act

    read_data_spy.assert_not_called()
    write_ids_spy.assert_not_called()


def test_set_export_params(service_context, parameters_data_from_dict):
    service = ParametersService(service_context)

    export_query = service.set_export_params()  # act

    assert export_query == {"scope": parameters_data_from_dict.scope}
