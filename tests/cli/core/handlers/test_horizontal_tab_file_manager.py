from collections.abc import Generator
from dataclasses import dataclass
from typing import Any, Self
from unittest import mock
from unittest.mock import MagicMock, Mock, call

import pytest
from cli.core.handlers.excel_styles import (
    horizontal_tab_style,
    number_format_style,
)
from cli.core.handlers.horizontal_tab_file_manager import HorizontalTabFileManager
from cli.core.models.data_model import BaseDataModel
from openpyxl.worksheet.datavalidation import DataValidation


@dataclass
class FakeDataModel(BaseDataModel):
    id: str | None = None
    currency: str | None = None
    precision: int | None = None

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


class FakeHorizontalTabFileManager(HorizontalTabFileManager):
    _file_handler = Mock()
    _data_model = FakeDataModel
    _fields = ["ID", "styled_field", "field2"]
    _id_field = "ID"
    _required_tabs = ["Required tab"]
    _required_fields_by_tab = {"FakeTab": "ID"}
    _sheet_name = "FakeSheet"
    _data_validation_map = {"field2": Mock(spec=DataValidation)}

    def _read_data(self) -> Generator[dict[str, Any], None, None]:
        yield {"ID": "fake_id", "styled_field": 22.5, "field2": "fake field value"}


@pytest.fixture
def fake_horizontal_tab_file_manager():
    return FakeHorizontalTabFileManager("fake_path")


@pytest.mark.parametrize(
    ("currency", "precision", "expected_style"),
    [
        ("USD", 2, number_format_style),
        (None, None, None),
    ],
)
def test_add(mocker, currency, precision, expected_style, fake_horizontal_tab_file_manager):
    get_sheet_next_row_mock = mocker.patch.object(
        fake_horizontal_tab_file_manager.file_handler, "get_sheet_next_row", return_value=2
    )
    item = FakeDataModel(currency=currency, precision=precision)
    item_to_xlsx_mock = mocker.patch.object(
        item,
        "to_xlsx",
        return_value={"ID": "fake_id", "styled_field": 22.5, "field2": "fake field value"},
    )
    write_cell_mock = mocker.patch.object(
        fake_horizontal_tab_file_manager.file_handler, "write_cell"
    )
    save_mock = mocker.patch.object(fake_horizontal_tab_file_manager.file_handler, "save")

    fake_horizontal_tab_file_manager.add([item])

    get_sheet_next_row_mock.assert_called_once_with("FakeSheet")
    item_to_xlsx_mock.assert_called_once()
    write_cell_mock.assert_has_calls([
        call("FakeSheet", col=1, row=2, value="fake_id", data_validation=None, style=None),
        call(
            "FakeSheet",
            col=2,
            row=2,
            value=22.5,
            data_validation=None,
            style=expected_style,
        ),
        call(
            "FakeSheet",
            col=3,
            row=2,
            value="fake field value",
            data_validation=mock.ANY,
            style=None,
        ),
    ])
    save_mock.assert_called_once()


def test_add_no_style_attributes(mocker, fake_horizontal_tab_file_manager):
    mocker.patch.object(
        fake_horizontal_tab_file_manager.file_handler, "get_sheet_next_row", return_value=2
    )
    mocker.patch.object(fake_horizontal_tab_file_manager.file_handler, "save")
    item_mock = MagicMock(
        spec=BaseDataModel, to_xlsx=Mock(return_value={"ID": "fake_id", "styled_field": 22.5})
    )
    write_cell_mock = mocker.patch.object(
        fake_horizontal_tab_file_manager.file_handler, "write_cell"
    )

    fake_horizontal_tab_file_manager.add([item_mock])

    write_cell_mock.assert_has_calls([
        call("FakeSheet", col=1, row=2, value="fake_id", data_validation=None, style=None),
        call(
            "FakeSheet",
            col=2,
            row=2,
            value=22.5,
            data_validation=None,
            style=None,
        ),
    ])


def test_create_tab(mocker, fake_horizontal_tab_file_manager):
    file_handler = fake_horizontal_tab_file_manager.file_handler
    exists_mock = mocker.patch.object(file_handler, "exists", return_value=False)
    create_mock = mocker.patch.object(file_handler, "create")
    write_cell_mock = mocker.patch.object(file_handler, "write_cell")

    fake_horizontal_tab_file_manager.create_tab()

    exists_mock.assert_called_once()
    create_mock.assert_called_once()
    write_cell_mock.assert_has_calls([
        call("FakeSheet", row=1, col=1, value="ID", style=horizontal_tab_style),
        call("FakeSheet", row=1, col=2, value="styled_field", style=horizontal_tab_style),
        call("FakeSheet", row=1, col=3, value="field2", style=horizontal_tab_style),
    ])


def test_read_data(mocker, fake_horizontal_tab_file_manager):
    data_model_spy = mocker.spy(fake_horizontal_tab_file_manager._data_model, "from_dict")

    result = list(fake_horizontal_tab_file_manager.read_data())

    assert len(result) == 1
    assert result == [FakeDataModel()]
    data_model_spy.assert_called_once_with({
        "ID": "fake_id",
        "styled_field": 22.5,
        "field2": "fake field value",
    })


def test_write_error(mocker, fake_horizontal_tab_file_manager):
    file_handler = fake_horizontal_tab_file_manager.file_handler
    mock_data = {
        "ID": {"coordinate": "A4", "value": "fake_id"},
        "Error": {"coordinate": "H4", "value": ""},
    }
    get_data_from_horizontal_sheet_mock = mocker.patch.object(
        file_handler, "get_data_from_horizontal_sheet", return_value=iter([mock_data])
    )
    write_mock = mocker.patch.object(file_handler, "write")

    fake_horizontal_tab_file_manager.write_error("Test Error", "fake_id")

    get_data_from_horizontal_sheet_mock.assert_called_once()
    write_mock.assert_called_with([{"FakeSheet": {"H4": "Test Error"}}])


def test_write_error_no_column(mocker, fake_horizontal_tab_file_manager):
    file_handler = fake_horizontal_tab_file_manager.file_handler
    mock_data = {
        "ID": {"coordinate": "A4", "value": "fake_id"},
    }
    get_data_from_horizontal_sheet_mock = mocker.patch.object(
        file_handler, "get_data_from_horizontal_sheet", return_value=iter([mock_data])
    )
    get_sheet_next_column_mock = mocker.patch.object(
        file_handler, "get_sheet_next_column", return_value="P"
    )
    write_mock = mocker.patch.object(file_handler, "write")

    fake_horizontal_tab_file_manager.write_error("Test Error", "fake_id")

    get_data_from_horizontal_sheet_mock.assert_called_once()
    get_sheet_next_column_mock.assert_called_once()
    write_mock.assert_has_calls([
        call([{"FakeSheet": {"P1": "Error"}}]),
        call([{"FakeSheet": {"P4": "Test Error"}}]),
    ])
