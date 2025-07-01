from unittest.mock import Mock

import pytest
from swo.mpt.cli.core.errors import MPTAPIError
from swo.mpt.cli.core.models import BaseDataModel, DataCollectionModel
from swo.mpt.cli.core.products.services.related_components_base_service import (
    RelatedComponentsBaseService,
)
from swo.mpt.cli.core.services.service_context import ServiceContext
from swo.mpt.cli.core.services.service_result import ServiceResult
from swo.mpt.cli.core.stats import ProductStatsCollector


class FakeRelatedComponentsService(RelatedComponentsBaseService):
    def export(self) -> ServiceResult:
        pass

    def retrieve(self) -> ServiceResult:
        pass

    def retrieve_from_mpt(self, resource_id: str) -> ServiceResult:
        pass

    def update(self, resource_id: str) -> ServiceResult:
        pass


@pytest.fixture
def service_context(active_vendor_account):
    return ServiceContext(
        account=active_vendor_account,
        api=Mock(),
        data_model=BaseDataModel,
        file_manager=Mock(tab_name="fake_tab_name"),
        stats=ProductStatsCollector(),
    )


def test_create(mocker, service_context, mpt_parameters_data):
    data_model_mock = Mock(
        id="fake_id", coordinate="fake_coordinate", to_json=Mock(return_value={"id": "fake_id"})
    )
    new_item_mock = {"id": "new_fake_id"}
    mocker.patch.object(service_context.file_manager, "read_data", return_value=[data_model_mock])
    post_mock = mocker.patch.object(service_context.api, "post", return_value=new_item_mock)
    file_handler_write_id_mock = mocker.patch.object(service_context.file_manager, "write_id")
    stats_mock = mocker.patch.object(service_context.stats, "add_synced")
    service = FakeRelatedComponentsService(service_context)

    result = service.create()

    assert result.success is True
    assert result.model is None
    assert isinstance(result.collection, DataCollectionModel)
    file_handler_write_id_mock.assert_called_once_with("fake_coordinate", "new_fake_id")
    post_mock.assert_called_once_with(json={"id": "fake_id"})
    stats_mock.assert_called_once_with("fake_tab_name")


def test_create_api_error(mocker, service_context, parameters_data_from_dict):
    mocker.patch.object(service_context.file_manager, "read_data", return_value=[Mock()])
    post_mock = mocker.patch.object(
        service_context.api,
        "post",
        side_effect=MPTAPIError("API Error", "Error creating parameter"),
    )
    write_error_mock = mocker.patch.object(service_context.file_manager, "write_error")
    add_error_mock = mocker.patch.object(service_context.stats, "add_error")
    service = FakeRelatedComponentsService(service_context)

    result = service.create()

    assert result.success is False
    assert len(result.errors) == 1
    post_mock.assert_called_once()
    write_error_mock.assert_called_once()
    add_error_mock.assert_called_once_with("fake_tab_name")
