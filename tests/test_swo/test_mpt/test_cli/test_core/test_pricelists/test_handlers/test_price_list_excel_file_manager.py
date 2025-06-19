from unittest.mock import call

from swo.mpt.cli.core.handlers.excel_file_handler import ExcelFileHandler
from swo.mpt.cli.core.price_lists.constants import (
    ERROR_COLUMN_NAME,
    GENERAL_FIELDS,
    GENERAL_PRICELIST_ID,
    TAB_GENERAL,
)
from swo.mpt.cli.core.price_lists.handlers import PriceListExcelFileManager
from swo.mpt.cli.core.price_lists.models import PriceListData


def test_add(mocker, price_list_data_from_json):
    write_mock = mocker.patch.object(ExcelFileHandler, "write")
    handler = PriceListExcelFileManager("fake_file.xlsx")

    handler.add(price_list_data_from_json)

    write_mock.assert_called_once()


def test_create_tab(mocker):
    exists_mock = mocker.patch.object(ExcelFileHandler, "exists", return_value=True)
    write_cell_mock = mocker.patch.object(ExcelFileHandler, "write_cell")
    merge_cell_mock = mocker.patch.object(ExcelFileHandler, "merge_cells")
    write_mock = mocker.patch.object(ExcelFileHandler, "write")

    handler = PriceListExcelFileManager("fake_file.xlsx")

    handler.create_tab()

    exists_mock.assert_called_once()
    write_cell_mock.assert_called_once_with(
        TAB_GENERAL, 1, 1, "General Information", style=mocker.ANY
    )
    merge_cell_mock.assert_called_once_with(TAB_GENERAL, "A1:B1")
    assert write_mock.call_count == len(GENERAL_FIELDS)


def test_read_data(mocker, price_list_data_from_dict):
    mock_data = {"fake_field1": {"field"}}
    get_data_from_vertical_sheet_mock = mocker.patch.object(
        ExcelFileHandler, "get_data_from_vertical_sheet", return_value=mock_data
    )
    price_list_from_dict_mock = mocker.patch.object(
        PriceListData, "from_dict", return_value=price_list_data_from_dict
    )
    handler = PriceListExcelFileManager("fake_file.xlsx")

    result = handler.read_data()

    assert result == price_list_data_from_dict
    get_data_from_vertical_sheet_mock.assert_called_once_with(TAB_GENERAL, GENERAL_FIELDS)
    price_list_from_dict_mock.assert_called_once_with(mock_data)


def test_write_error_existing_column(mocker):
    mock_data = {ERROR_COLUMN_NAME: {"value": "Error", "coordinate": "B2"}}
    get_data_from_vertical_sheet_mock = mocker.patch.object(
        ExcelFileHandler, "get_data_from_vertical_sheet", return_value=mock_data
    )
    write_mock = mocker.patch.object(ExcelFileHandler, "write", return_value=None)
    handler = PriceListExcelFileManager("fake_file.xlsx")

    handler.write_error("fake error message")

    get_data_from_vertical_sheet_mock.assert_called_once_with(
        TAB_GENERAL, [GENERAL_PRICELIST_ID, ERROR_COLUMN_NAME]
    )
    write_mock.assert_called_with([{TAB_GENERAL: {"B2": "fake error message"}}])


def test_write_error_missing_column(mocker):
    mock_data = {"no_data_column": {"value": "fake_value", "coordinate": "AA125"}}
    get_data_from_vertical_sheet_mock = mocker.patch.object(
        ExcelFileHandler, "get_data_from_vertical_sheet", return_value=mock_data
    )
    get_sheet_next_column_mock = mocker.patch.object(
        ExcelFileHandler, "get_sheet_next_column", return_value="AB"
    )
    write_mock = mocker.patch.object(ExcelFileHandler, "write")
    handler = PriceListExcelFileManager("fake_file.xlsx")

    handler.write_error("fake error message")

    get_data_from_vertical_sheet_mock.assert_called_once_with(
        TAB_GENERAL, [GENERAL_PRICELIST_ID, ERROR_COLUMN_NAME]
    )
    get_sheet_next_column_mock.assert_called_once_with(TAB_GENERAL)
    write_mock.assert_has_calls(
        [
            call([{TAB_GENERAL: {"AB1": ERROR_COLUMN_NAME}}]),
            call([{TAB_GENERAL: {"AB125": "fake error message"}}]),
        ]
    )
