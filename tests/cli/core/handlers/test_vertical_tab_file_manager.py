from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Self
from unittest.mock import Mock, call

import pytest
from cli.core.handlers.excel_styles import general_tab_title_style
from cli.core.handlers.vertical_tab_file_manager import VerticalTabFileManager
from cli.core.models import BaseDataModel
from cli.core.products.constants import (
    ERROR_COLUMN_NAME,
)


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


class FakeVerticalTabFileManager(VerticalTabFileManager):
    _file_handler = Mock()
    _data_model = FakeDataModel
    _fields = ("ID", "field1")
    _id_field = "ID"
    _required_tabs = ("Required tab",)
    _required_fields_by_tab = MappingProxyType({"FakeSheet": ["ID"]})
    _sheet_name = "FakeSheet"


@pytest.fixture
def file_manager():
    return FakeVerticalTabFileManager("fake_path")


def test_add(mocker, file_manager):
    to_xlsx_mock = mocker.patch.object(FakeDataModel, "to_xlsx", return_value={"ID": "fake_id"})
    write_mock = mocker.patch.object(file_manager.file_handler, "write")

    file_manager.add(FakeDataModel())  # act

    to_xlsx_mock.assert_called_once()
    write_mock.assert_called_once_with([{"FakeSheet": {"B2": "fake_id", "B3": ""}}])


def test_check_required_tabs(mocker, file_manager):
    check_required_sheet_mock = mocker.patch.object(
        file_manager.file_handler, "check_required_sheet"
    )

    file_manager.check_required_tabs()  # act

    check_required_sheet_mock.assert_called_once_with(("Required tab",))


def test_check_required_fields_by_section(mocker, file_manager):
    check_required_fields_in_vertical_mock = mocker.patch.object(
        file_manager.file_handler, "check_required_fields_in_vertical_sheet"
    )
    check_required_field_values_mock = mocker.patch.object(
        file_manager.file_handler, "check_required_field_values_in_vertical_sheet"
    )
    check_required_fields_in_horizontal_mock = mocker.patch.object(
        file_manager.file_handler, "check_required_fields_in_horizontal_sheet"
    )

    file_manager.check_required_fields_by_section()  # act

    check_required_fields_in_vertical_mock.assert_called_once()
    check_required_field_values_mock.assert_called_once()
    check_required_fields_in_horizontal_mock.assert_not_called()


def test_create_tab(mocker, file_manager):
    exists_mock = mocker.patch.object(file_manager.file_handler, "exists", return_value=True)
    write_cell_mock = mocker.patch.object(file_manager.file_handler, "write_cell")
    merge_cell_mock = mocker.patch.object(file_manager.file_handler, "merge_cells")
    write_mock = mocker.patch.object(file_manager.file_handler, "write")

    file_manager.create_tab()  # act

    exists_mock.assert_called_once()
    write_cell_mock.assert_called_once_with(
        "FakeSheet", 1, 1, "General Information", style=general_tab_title_style
    )
    merge_cell_mock.assert_called_once_with("FakeSheet", "A1:B1")
    write_mock.assert_has_calls([
        call([{"FakeSheet": {"A2": "ID"}}]),
        call([{"FakeSheet": {"A3": "field1"}}]),
    ])


def test_read_data(mocker, file_manager):
    mock_data = {"fake_field1": {"field"}}
    get_data_from_vertical_sheet_mock = mocker.patch.object(
        file_manager.file_handler, "get_data_from_vertical_sheet", return_value=mock_data
    )
    data_model_spy = mocker.spy(file_manager._data_model, "from_dict")  # noqa: SLF001

    result = file_manager.read_data()

    assert result == FakeDataModel()
    data_model_spy.assert_called_once()
    get_data_from_vertical_sheet_mock.assert_called_once()


def test_write_error_existing_column(mocker, file_manager):
    mock_data = {ERROR_COLUMN_NAME: {"value": "Error", "coordinate": "B2"}}
    get_data_from_vertical_sheet_mock = mocker.patch.object(
        file_manager.file_handler, "get_data_from_vertical_sheet", return_value=mock_data
    )
    write_mock = mocker.patch.object(file_manager.file_handler, "write", return_value=None)

    file_manager.write_error("fake error message")  # act

    get_data_from_vertical_sheet_mock.assert_called_once_with(
        "FakeSheet", ("ID", ERROR_COLUMN_NAME)
    )
    write_mock.assert_called_with([{"FakeSheet": {"B2": "fake error message"}}])


def test_write_error_missing_column(mocker, file_manager):
    mock_data = {"no_data_column": {"value": "fake_value", "coordinate": "AA125"}}
    get_data_from_vertical_sheet_mock = mocker.patch.object(
        file_manager.file_handler, "get_data_from_vertical_sheet", return_value=mock_data
    )
    get_sheet_next_column_mock = mocker.patch.object(
        file_manager.file_handler, "get_sheet_next_column", return_value="AB"
    )
    write_mock = mocker.patch.object(file_manager.file_handler, "write")

    file_manager.write_error("fake error message")  # act

    get_data_from_vertical_sheet_mock.assert_called_once_with(
        "FakeSheet", ("ID", ERROR_COLUMN_NAME)
    )
    get_sheet_next_column_mock.assert_called_once_with("FakeSheet")
    write_mock.assert_has_calls([
        call([{"FakeSheet": {"AB1": ERROR_COLUMN_NAME}}]),
        call([{"FakeSheet": {"AB125": "fake error message"}}]),
    ])
