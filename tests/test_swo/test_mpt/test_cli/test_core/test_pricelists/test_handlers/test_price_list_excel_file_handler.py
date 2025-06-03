from unittest.mock import call

from swo.mpt.cli.core.handlers.excel_file_handler import ExcelFileHandler
from swo.mpt.cli.core.price_lists.constants import (
    ERROR_COLUMN_NAME,
    GENERAL_FIELDS,
    GENERAL_PRICELIST_ID,
    PRICELIST_ITEMS_FIELDS,
    TAB_GENERAL,
    TAB_PRICE_ITEMS,
)
from swo.mpt.cli.core.price_lists.handlers.price_list_excel_file_handler import (
    PriceListExcelFileHandler,
)
from swo.mpt.cli.core.price_lists.models import ItemData, PriceListData


def test_read_general_data(mocker, price_list_data_from_dict):
    mock_data = {"fake_field1": {"field"}}
    get_data_from_vertical_sheet_mock = mocker.patch.object(
        ExcelFileHandler, "get_data_from_vertical_sheet", return_value=mock_data
    )
    price_list_from_dict_mock = mocker.patch.object(
        PriceListData, "from_dict", return_value=price_list_data_from_dict
    )
    handler = PriceListExcelFileHandler("fake_file.xlsx")

    result = handler.read_general_data()

    assert result == price_list_data_from_dict
    get_data_from_vertical_sheet_mock.assert_called_once_with(TAB_GENERAL, GENERAL_FIELDS)
    price_list_from_dict_mock.assert_called_once_with(mock_data)


def test_read_items_data(mocker, item_data_from_dict):
    mock_data = {"fake_field1": {"field"}}
    get_data_from_horizontal_sheet_mock = mocker.patch.object(
        ExcelFileHandler, "get_data_from_horizontal_sheet", return_value=iter([mock_data])
    )
    item_data_from_dict_mock = mocker.patch.object(
        ItemData, "from_dict", return_value=item_data_from_dict
    )
    handler = PriceListExcelFileHandler("fake_file.xlsx")

    result = list(handler.read_items_data())

    assert result == [item_data_from_dict]
    get_data_from_horizontal_sheet_mock.assert_called_once_with(
        TAB_PRICE_ITEMS, PRICELIST_ITEMS_FIELDS
    )
    item_data_from_dict_mock.assert_called_once_with(mock_data)


def test_write_id(mocker):
    write_id_mock = mocker.patch.object(ExcelFileHandler, "write", return_value=None)
    handler = PriceListExcelFileHandler("fake_file.xlsx")

    handler.write_id("J12", "new_id")

    write_id_mock.assert_called_once_with([{TAB_GENERAL: {"J12": "new_id"}}])


def test_write_error_existing_column(mocker):
    mock_data = {ERROR_COLUMN_NAME: {"value": "Error", "coordinate": "B2"}}
    get_data_from_vertical_sheet_mock = mocker.patch.object(
        ExcelFileHandler, "get_data_from_vertical_sheet", return_value=mock_data
    )
    write_mock = mocker.patch.object(ExcelFileHandler, "write", return_value=None)
    handler = PriceListExcelFileHandler("fake_file.xlsx")

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
    handler = PriceListExcelFileHandler("fake_file.xlsx")

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
