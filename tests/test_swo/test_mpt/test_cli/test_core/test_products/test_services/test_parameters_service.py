import pytest
from swo.mpt.cli.core.models import DataCollectionModel
from swo.mpt.cli.core.products.api import ParametersAPIService
from swo.mpt.cli.core.products.handlers import AgreementParametersExcelFileManager
from swo.mpt.cli.core.products.models import AgreementParametersData
from swo.mpt.cli.core.products.services import ParametersService
from swo.mpt.cli.core.services.service_context import ServiceContext
from swo.mpt.cli.core.stats import ProductStatsCollector


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
    write_id_mock = mocker.patch.object(service_context.file_manager, "write_id")
    service = ParametersService(service_context)

    service.set_new_parameter_group(param_group)

    read_data_mock.assert_called_once()
    write_id_mock.assert_called_once_with(
        parameters_data_from_dict.group_id_coordinate, parameter_group_data_from_dict.id
    )


def test_set_new_parameter_groups_error(
    mocker, service_context, parameters_data_from_dict, parameter_group_data_from_dict
):
    read_data_mock = mocker.patch.object(
        service_context.file_manager, "read_data", return_value=[parameters_data_from_dict]
    )
    param_group = DataCollectionModel(collection={"not_found_key": parameter_group_data_from_dict})
    write_id_mock = mocker.patch.object(service_context.file_manager, "write_id")
    service = ParametersService(service_context)

    service.set_new_parameter_group(param_group)

    read_data_mock.assert_called_once()
    write_id_mock.assert_not_called()


def test_set_new_parameter_groups_empty(mocker, service_context):
    read_data_spy = mocker.spy(service_context.file_manager, "read_data")
    write_id_spy = mocker.spy(service_context.file_manager, "write_id")
    service = ParametersService(service_context)

    service.set_new_parameter_group(DataCollectionModel(collection={}))

    read_data_spy.assert_not_called()
    write_id_spy.assert_not_called()


def test_set_export_params(service_context, parameters_data_from_dict):
    service = ParametersService(service_context)

    params = service.set_export_params()

    assert params == {"scope": parameters_data_from_dict.scope}
