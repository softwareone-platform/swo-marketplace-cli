from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Self
from unittest.mock import Mock

import pytest
from cli.core.errors import MPTAPIError
from cli.core.models import BaseDataModel, DataCollectionModel
from cli.core.products.models import DataActionEnum
from cli.core.products.services.related_components_base_service import (
    RelatedComponentsBaseService,
)
from cli.core.services.service_context import ServiceContext
from cli.core.stats import ProductStatsCollector


class FakeRelatedComponentsService(RelatedComponentsBaseService):
    """Fake related components service."""


class FakeActionEnum(StrEnum):
    FAKE_ACTION = "fake_action"


@dataclass
class FakeDataModel(BaseDataModel):
    id: str = "fake_id"
    coordinate: str = "fake_coordinate"
    action: FakeActionEnum = FakeActionEnum.FAKE_ACTION

    @property
    def to_skip(self):
        return False

    @classmethod
    def from_dict(cls, row_data: dict[str, Any]) -> Self:
        return cls()

    @classmethod
    def from_json(cls, json_data: dict[str, Any]) -> Self:
        return cls()

    def to_json(self) -> dict[str, Any]:
        return {"id": self.id}

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


def test_create(mocker, service_context, mpt_agreement_parameter_data):
    data_model_mock = FakeDataModel()
    new_item_mock = {"id": "new_fake_id"}
    mocker.patch.object(service_context.file_manager, "read_data", return_value=[data_model_mock])
    post_mock = mocker.patch.object(service_context.api, "post", return_value=new_item_mock)
    write_ids_mock = mocker.patch.object(service_context.file_manager, "write_ids")
    stats_mock = mocker.patch.object(service_context.stats, "add_synced")
    service = FakeRelatedComponentsService(service_context)
    prepare_data_model_to_create_spy = mocker.spy(service, "prepare_data_model_to_create")

    result = service.create()

    assert result.success is True
    assert result.model is None
    assert isinstance(result.collection, DataCollectionModel)
    write_ids_mock.assert_called_once_with({"fake_coordinate": "new_fake_id"})
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


def test_export(mocker, service_context, mpt_agreement_parameter_data):
    create_data_mock = mocker.patch.object(service_context.file_manager, "create_tab")
    response_payload = {"meta": {"offset": 0, "limit": 100, "total": 0}, "data": []}
    api_list_mock = mocker.patch.object(service_context.api, "list", return_value=response_payload)
    add_mock = mocker.patch.object(service_context.file_manager, "add")
    service = FakeRelatedComponentsService(service_context)

    result = service.export()

    assert result.success is True
    assert result.model is None
    create_data_mock.assert_called_once()
    api_list_mock.assert_called_once()
    add_mock.assert_called_once()


def test_export_error(mocker, service_context, mpt_agreement_parameter_data):
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


def test_update_action_skip(mocker, service_context):
    mocker.patch.object(
        service_context.file_manager,
        "read_data",
        return_value=[FakeDataModel(id="skip_item_id", action=DataActionEnum.SKIP)],
    )
    mocker.patch.object(FakeDataModel, "to_skip", new=True)
    stats_skipped_mock = mocker.patch.object(service_context.stats, "add_skipped")
    service = FakeRelatedComponentsService(service_context)

    result = service.update()

    assert result.success is True
    assert result.model is None
    stats_skipped_mock.assert_called_once_with("fake_tab_name")


def test_update_action_create(mocker, service_context):
    mocker.patch.object(
        service_context.file_manager,
        "read_data",
        return_value=[FakeDataModel(id="create_id", action=DataActionEnum.CREATE)],
    )
    mocker.patch.object(FakeDataModel, "to_skip", new=False)
    write_ids_mock = mocker.patch.object(service_context.file_manager, "write_ids")
    stats_synced_mock = mocker.patch.object(service_context.stats, "add_synced")
    api_post_mock = mocker.patch.object(
        service_context.api, "post", return_value={"id": "new_fake_id"}
    )
    service = FakeRelatedComponentsService(service_context)

    result = service.update()

    assert result.success is True
    assert result.model is None
    write_ids_mock.assert_called_once_with({"fake_coordinate": "new_fake_id"})
    stats_synced_mock.assert_called_once_with("fake_tab_name")
    api_post_mock.assert_called_once_with(json={"id": "create_id"})


def test_update_action_delete(mocker, service_context):
    mocker.patch.object(
        service_context.file_manager,
        "read_data",
        return_value=[FakeDataModel(id="delete_id", action=DataActionEnum.DELETE)],
    )
    mocker.patch.object(FakeDataModel, "to_skip", new=False)
    file_handler_error_mock = mocker.patch.object(service_context.file_manager, "write_error")
    stats_error_mock = mocker.patch.object(service_context.stats, "add_error")
    service = FakeRelatedComponentsService(service_context)

    result = service.update()

    assert result.success is False
    file_handler_error_mock.assert_called_once_with(
        "Action type delete is not supported", "delete_id"
    )
    stats_error_mock.assert_called_once_with("fake_tab_name")


def test_update_action_update(mocker, service_context):
    mocker.patch.object(
        service_context.file_manager,
        "read_data",
        return_value=[FakeDataModel(id="update_id", action=DataActionEnum.UPDATE)],
    )
    mocker.patch.object(FakeDataModel, "to_skip", new=False)
    write_ids_mock = mocker.patch.object(service_context.file_manager, "write_ids")
    stats_synced_mock = mocker.patch.object(service_context.stats, "add_synced")
    api_update_mock = mocker.patch.object(service_context.api, "update")
    service = FakeRelatedComponentsService(service_context)

    result = service.update()

    assert result.success is True
    assert result.model is None
    write_ids_mock.assert_called_once_with({"fake_coordinate": "update_id"})
    stats_synced_mock.assert_called_once_with("fake_tab_name")
    api_update_mock.assert_called_once_with("update_id", {"id": "update_id"})


def test_update_action_value_error(mocker, service_context):
    mocker.patch.object(
        service_context.file_manager,
        "read_data",
        return_value=[FakeDataModel(id="error_action_id", action="FakeAction")],
    )
    mocker.patch.object(FakeDataModel, "to_skip", new=False)
    file_handler_error_mock = mocker.patch.object(service_context.file_manager, "write_error")
    stats_error_mock = mocker.patch.object(service_context.stats, "add_error")
    service = FakeRelatedComponentsService(service_context)

    result = service.update()

    assert result.success is False
    file_handler_error_mock.assert_called_once_with("Invalid action: FakeAction", "error_action_id")
    stats_error_mock.assert_called_once_with("fake_tab_name")


def test_update_action_api_error(mocker, service_context):
    mocker.patch.object(
        service_context.file_manager,
        "read_data",
        return_value=[FakeDataModel(id="update_id", action=DataActionEnum.UPDATE)],
    )
    mocker.patch.object(FakeDataModel, "to_skip", new=False)
    file_handler_error_mock = mocker.patch.object(service_context.file_manager, "write_error")
    stats_error_mock = mocker.patch.object(service_context.stats, "add_error")
    api_update_mock = mocker.patch.object(
        service_context.api, "update", side_effect=MPTAPIError("API Error", "Error updating item")
    )
    service = FakeRelatedComponentsService(service_context)

    result = service.update()

    assert result.success is False
    file_handler_error_mock.assert_called_once_with(
        "API Error with response body Error updating item", "update_id"
    )
    stats_error_mock.assert_called_once_with("fake_tab_name")
    api_update_mock.assert_called_once_with("update_id", {"id": "update_id"})
