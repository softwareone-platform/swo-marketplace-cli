from dataclasses import dataclass
from typing import Any, Self
from unittest.mock import Mock

import pytest
from swo.mpt.cli.core.errors import MPTAPIError
from swo.mpt.cli.core.models import BaseDataModel, DataCollectionModel
from swo.mpt.cli.core.products.services.related_components_base_service import (
    RelatedComponentsBaseService,
)
from swo.mpt.cli.core.services.service_context import ServiceContext
from swo.mpt.cli.core.stats import ProductStatsCollector


class FakeRelatedComponentsService(RelatedComponentsBaseService):
    pass


@dataclass
class FakeDataModel(BaseDataModel):
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls()

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        return cls()

    def to_json(self) -> dict[str, Any]:
        return {}

    def to_xlsx(self) -> dict[str, Any]:
        return {}


@pytest.fixture
def service_context(active_vendor_account):
    return ServiceContext(
        account=active_vendor_account,
        api=Mock(),
        data_model=FakeDataModel,
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
    prepare_data_model_to_create_spy = mocker.spy(service, "prepare_data_model_to_create")

    result = service.create()

    assert result.success is True
    assert result.model is None
    assert isinstance(result.collection, DataCollectionModel)
    file_handler_write_id_mock.assert_called_once_with("fake_coordinate", "new_fake_id")
    post_mock.assert_called_once_with(json={"id": "fake_id"})
    stats_mock.assert_called_once_with("fake_tab_name")
    prepare_data_model_to_create_spy.assert_called_once()


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


def test_export(mocker, service_context, mpt_parameters_data):
    create_data_mock = mocker.patch.object(service_context.file_manager, "create_tab")
    data = {"meta": {"offset": 0, "limit": 100, "total": 0}, "data": []}
    api_list_mock = mocker.patch.object(service_context.api, "list", return_value=data)
    add_mock = mocker.patch.object(service_context.file_manager, "add")
    service = FakeRelatedComponentsService(service_context)

    result = service.export()

    assert result.success is True
    assert result.model is None
    create_data_mock.assert_called_once()
    api_list_mock.assert_called_once()
    add_mock.assert_called_once()


def test_export_error(mocker, service_context, mpt_parameters_data):
    create_data_mock = mocker.patch.object(service_context.file_manager, "create_tab")
    api_list_mock = mocker.patch.object(
        service_context.api,
        "list",
        side_effect=MPTAPIError("API Error", "Error getting parameters"),
    )
    write_error_mock = mocker.patch.object(service_context.file_manager, "write_error")
    add_error_mock = mocker.patch.object(service_context.stats, "add_error")
    add_spy = mocker.spy(service_context.file_manager, "add")
    service = FakeRelatedComponentsService(service_context)

    result = service.export()

    assert result.success is False
    assert result.errors == ["API Error with response body Error getting parameters"]
    create_data_mock.assert_called_once()
    api_list_mock.assert_called_once()
    add_error_mock.assert_called_once_with("fake_tab_name")
    write_error_mock.assert_called_once()
    add_spy.assert_not_called()
