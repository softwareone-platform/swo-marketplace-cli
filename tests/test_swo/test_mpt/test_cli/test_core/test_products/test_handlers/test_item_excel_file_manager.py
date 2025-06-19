import re
from unittest.mock import call

from swo.mpt.cli.core.handlers.excel_file_handler import ExcelFileHandler
from swo.mpt.cli.core.products.constants import (
    ERROR_COLUMN_NAME,
    ITEMS_FIELDS,
    ITEMS_ID,
    TAB_ITEMS,
)
from swo.mpt.cli.core.products.handlers import ItemExcelFileManager
from swo.mpt.cli.core.products.models import ItemData


def test_create_tab(mocker):
    exists_mock = mocker.patch.object(ExcelFileHandler, "exists", return_value=False)
    create_mock = mocker.patch.object(ExcelFileHandler, "create")
    write_cell_mock = mocker.patch.object(ExcelFileHandler, "write_cell")
    handler = ItemExcelFileManager("fake_file.xlsx")

    handler.create_tab()

    exists_mock.assert_called_once()
    create_mock.assert_called_once()
    assert write_cell_mock.call_count == len(ITEMS_FIELDS)


def test_read_data(mocker, item_data_from_dict):
    mock_data = {"fake_field1": {"field"}}
    get_values_for_dynamic_sheet_mock = mocker.patch.object(
        ExcelFileHandler, "get_values_for_dynamic_sheet", return_value=iter([mock_data])
    )
    item_data_from_dict_mock = mocker.patch.object(
        ItemData, "from_dict", return_value=item_data_from_dict
    )
    handler = ItemExcelFileManager("fake_file.xlsx")

    result = list(handler.read_data())

    assert result == [item_data_from_dict]
    get_values_for_dynamic_sheet_mock.assert_called_once_with(
        TAB_ITEMS, ITEMS_FIELDS, [re.compile(r"Parameter\.*")]
    )
    item_data_from_dict_mock.assert_called_once_with(mock_data)


def test_write_error_existing_column(mocker, item_data_from_dict):
    mock_data = {
        "ID": {"value": item_data_from_dict.id, "coordinate": "A2"},
        ERROR_COLUMN_NAME: {"value": "Error", "coordinate": "O2"},
    }
    get_data_from_horizontal_sheet_mock = mocker.patch.object(
        ExcelFileHandler, "get_data_from_horizontal_sheet", return_value=iter([mock_data])
    )
    write_mock = mocker.patch.object(ExcelFileHandler, "write")
    handler = ItemExcelFileManager("fake_file.xlsx")

    handler.write_error("fake error message", item_data_from_dict.id)

    get_data_from_horizontal_sheet_mock.assert_called_once_with(
        TAB_ITEMS, [ITEMS_ID, ERROR_COLUMN_NAME]
    )
    write_mock.assert_called_once_with([{TAB_ITEMS: {"O2": "fake error message"}}])


def test_write_error_missing_column(mocker, item_data_from_dict):
    mock_data = {"ID": {"value": item_data_from_dict.id, "coordinate": "A19"}}
    get_data_from_horizontal_sheet_mock = mocker.patch.object(
        ExcelFileHandler, "get_data_from_horizontal_sheet", return_value=iter([mock_data])
    )
    get_sheet_next_column_mock = mocker.patch.object(
        ExcelFileHandler, "get_sheet_next_column", return_value="W"
    )
    write_mock = mocker.patch.object(ExcelFileHandler, "write")
    handler = ItemExcelFileManager("fake_file.xlsx")

    handler.write_error("fake error message", item_data_from_dict.id)

    get_data_from_horizontal_sheet_mock.assert_called_once_with(
        TAB_ITEMS, [ITEMS_ID, ERROR_COLUMN_NAME]
    )
    get_sheet_next_column_mock.assert_called_once_with(TAB_ITEMS)
    write_mock.assert_has_calls(
        [
            call([{TAB_ITEMS: {"W1": ERROR_COLUMN_NAME}}]),
            call([{TAB_ITEMS: {"W19": "fake error message"}}]),
        ]
    )
