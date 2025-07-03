import pytest
from swo.mpt.cli.core.models import DataCollectionModel
from swo.mpt.cli.core.products.api import TemplateAPIService
from swo.mpt.cli.core.products.handlers import TemplateExcelFileManager
from swo.mpt.cli.core.products.models import TemplateData
from swo.mpt.cli.core.products.services.template_service import TemplateService
from swo.mpt.cli.core.services.service_context import ServiceContext
from swo.mpt.cli.core.stats import ProductStatsCollector


@pytest.fixture
def service_context(mpt_client, product_file_path, active_vendor_account, template_data_from_dict):
    return ServiceContext(
        account=active_vendor_account,
        api=TemplateAPIService(mpt_client, resource_id="test-product-id"),
        data_model=TemplateData,
        file_manager=TemplateExcelFileManager(product_file_path),
        stats=ProductStatsCollector(),
    )


def test_set_new_parameter_group(
    mocker, service_context, template_data_from_dict, parameter_group_data_from_dict
):
    read_data_mock = mocker.patch.object(
        service_context.file_manager, "read_data", return_value=[template_data_from_dict]
    )
    param_group = DataCollectionModel(
        collection={"old_param_id": parameter_group_data_from_dict, "no_id": None}
    )
    template_data_from_dict.content = "old_param_id: bla"
    write_id_mock = mocker.patch.object(service_context.file_manager, "write_id")
    service = TemplateService(service_context)

    service.set_new_parameter_group(param_group)

    read_data_mock.assert_called_once()
    write_id_mock.assert_called_once_with(
        template_data_from_dict.content_coordinate, f"{parameter_group_data_from_dict.id}: bla"
    )


def test_set_new_parameter_groups_empty(mocker, service_context):
    read_data_spy = mocker.spy(service_context.file_manager, "read_data")
    write_id_spy = mocker.spy(service_context.file_manager, "write_id")
    service = TemplateService(service_context)

    service.set_new_parameter_group(DataCollectionModel(collection={}))

    read_data_spy.assert_not_called()
    write_id_spy.assert_not_called()
